"""
翻译引擎
核心翻译逻辑实现
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterator
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from translator.config import get_settings
from translator.config.languages import LanguageRegistry
from translator.core.exceptions import (
    ModelInferenceError,
    ModelLoadError,
    UnsupportedLanguageError,
)
from translator.core.models import (
    BatchResult,
    FileFormat,
    TranslationRequest,
    TranslationResult,
    TranslationStatus,
)
from translator.utils import FileHandler, get_logger

logger = get_logger(__name__)


class TranslationEngine:
    """翻译引擎"""

    def __init__(
        self,
        model_name: str | None = None,
        use_bfloat16: bool | None = None,
        device_map: str | None = None,
        max_new_tokens: int | None = None,
    ):
        """
        初始化翻译引擎

        Args:
            model_name: 模型名称或路径，None 使用配置默认值
            use_bfloat16: 是否使用 bfloat16，None 使用配置默认值
            device_map: 设备映射策略
            max_new_tokens: 最大生成 token 数
        """
        settings = get_settings()

        # 优先使用本地模型路径
        self.model_name = model_name or settings.model.get_model_name_or_path()
        self.use_bfloat16 = (
            use_bfloat16 if use_bfloat16 is not None else settings.model.use_bfloat16
        )
        self.device_map = device_map or settings.model.device_map
        self.max_new_tokens = max_new_tokens or settings.model.max_new_tokens

        self._model = None
        self._tokenizer = None
        self._loaded = False

        logger.debug(f"Engine initialized with model: {self.model_name}")

    @property
    def is_loaded(self) -> bool:
        """模型是否已加载"""
        return self._loaded

    @property
    def device(self) -> str:
        """当前设备"""
        if self._model:
            return str(self._model.device)
        return "not loaded"

    def load(self) -> TranslationEngine:
        """
        加载模型

        Returns:
            self，支持链式调用

        Raises:
            ModelLoadError: 模型加载失败
        """
        if self._loaded:
            logger.warning("Model already loaded, skipping")
            return self

        logger.info(f"Loading model: {self.model_name}")
        logger.info(f"Using bfloat16: {self.use_bfloat16}")

        try:
            # 加载 tokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)

            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token

            # 模型加载配置
            model_kwargs = {"device_map": self.device_map}

            if self.use_bfloat16 and torch.cuda.is_available():
                model_kwargs["torch_dtype"] = torch.bfloat16
                logger.info("CUDA available, using bfloat16")
            elif self.use_bfloat16:
                logger.warning("CUDA not available, bfloat16 disabled")

            # 加载模型
            self._model = AutoModelForCausalLM.from_pretrained(self.model_name, **model_kwargs)

            self._loaded = True
            logger.info(f"Model loaded successfully on device: {self.device}")

            return self

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise ModelLoadError(f"Failed to load model: {e}", model_name=self.model_name)

    def unload(self) -> None:
        """卸载模型释放资源"""
        if self._model:
            del self._model
            self._model = None
        if self._tokenizer:
            del self._tokenizer
            self._tokenizer = None

        self._loaded = False

        # 清理 GPU 缓存
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        logger.info("Model unloaded")

    def translate(self, request: TranslationRequest) -> TranslationResult:
        """
        执行翻译

        Args:
            request: 翻译请求

        Returns:
            翻译结果

        Raises:
            ModelInferenceError: 推理失败
            UnsupportedLanguageError: 不支持的语言方向
        """
        if not self._loaded:
            raise ModelInferenceError("Model not loaded. Call load() first.")

        start_time = time.perf_counter()

        # 获取语言方向配置
        direction = LanguageRegistry.get(request.direction)
        if direction is None and request.custom_prompt is None:
            raise UnsupportedLanguageError(
                request.direction, supported=LanguageRegistry.get_codes()
            )

        # 构建提示词
        prompt = request.custom_prompt or direction.prompt
        full_content = f"{prompt}\n\n{request.text}"

        messages = [{"role": "user", "content": full_content}]

        try:
            # 编码输入
            tokenized_chat = self._tokenizer.apply_chat_template(
                messages, tokenize=True, add_generation_prompt=False, return_tensors="pt"
            )

            # 生成翻译
            outputs = self._model.generate(
                tokenized_chat.to(self._model.device),
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                pad_token_id=self._tokenizer.pad_token_id,
            )

            # 解码输出
            output_text = self._tokenizer.decode(outputs[0], skip_special_tokens=True)

            # 提取翻译结果
            translated = self._extract_translation(output_text, request.text)

            processing_time = (time.perf_counter() - start_time) * 1000

            return TranslationResult(
                source_text=request.text,
                translated_text=translated,
                direction=request.direction,
                status=TranslationStatus.COMPLETED,
                processing_time_ms=processing_time,
                token_count=outputs.shape[-1],
            )

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return TranslationResult(
                source_text=request.text,
                translated_text="",
                direction=request.direction,
                status=TranslationStatus.FAILED,
                error_message=str(e),
                processing_time_ms=(time.perf_counter() - start_time) * 1000,
            )

    def _extract_translation(self, full_output: str, original_text: str) -> str:
        """从完整输出中提取翻译结果"""
        if original_text in full_output:
            parts = full_output.split(original_text)
            if len(parts) > 1:
                result = parts[-1].strip()
                return result if result else full_output
        return full_output.strip()

    def translate_text(
        self, text: str, direction: str = "en2zh", custom_prompt: str | None = None
    ) -> str:
        """
        便捷翻译方法

        Args:
            text: 待翻译文本
            direction: 翻译方向
            custom_prompt: 自定义提示词

        Returns:
            翻译结果文本
        """
        request = TranslationRequest(text=text, direction=direction, custom_prompt=custom_prompt)
        result = self.translate(request)

        if result.status == TranslationStatus.FAILED:
            raise ModelInferenceError(result.error_message or "Translation failed")

        return result.translated_text

    def translate_batch(
        self,
        texts: list[str],
        direction: str = "en2zh",
        custom_prompt: str | None = None,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> BatchResult:
        """
        批量翻译

        Args:
            texts: 待翻译文本列表
            direction: 翻译方向
            custom_prompt: 自定义提示词
            on_progress: 进度回调 (current, total)

        Returns:
            批量结果
        """
        batch_result = BatchResult(total=len(texts))

        for i, text in enumerate(texts):
            request = TranslationRequest(
                text=text, direction=direction, custom_prompt=custom_prompt
            )
            result = self.translate(request)
            batch_result.add_result(result)

            if on_progress:
                on_progress(i + 1, len(texts))

        return batch_result

    def translate_stream(
        self, texts: list[str], direction: str = "en2zh", custom_prompt: str | None = None
    ) -> Iterator[TranslationResult]:
        """
        流式翻译（生成器）

        Args:
            texts: 待翻译文本列表
            direction: 翻译方向
            custom_prompt: 自定义提示词

        Yields:
            每个翻译结果
        """
        for text in texts:
            request = TranslationRequest(
                text=text, direction=direction, custom_prompt=custom_prompt
            )
            yield self.translate(request)

    def translate_file(
        self,
        input_path: Path | str,
        output_path: Path | str,
        direction: str = "en2zh",
        format: FileFormat | None = None,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> BatchResult:
        """
        翻译文件

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            direction: 翻译方向
            format: 文件格式
            on_progress: 进度回调

        Returns:
            批量结果
        """
        handler = FileHandler()

        # 读取输入
        logger.info(f"Reading from: {input_path}")
        texts = handler.read(input_path, format)
        logger.info(f"Found {len(texts)} texts to translate")

        # 批量翻译
        batch_result = self.translate_batch(texts, direction=direction, on_progress=on_progress)

        # 写入输出
        translated_texts = [r.translated_text for r in batch_result.results]
        handler.write(output_path, translated_texts, format)

        logger.info(f"Translation completed. Saved to: {output_path}")

        return batch_result

    def __enter__(self) -> TranslationEngine:
        """上下文管理器入口"""
        return self.load()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """上下文管理器退出"""
        self.unload()
