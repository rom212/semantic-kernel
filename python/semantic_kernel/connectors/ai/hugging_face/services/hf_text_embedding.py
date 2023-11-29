# Copyright (c) Microsoft. All rights reserved.

from logging import Logger
from typing import List, Optional

import sentence_transformers
import torch
from numpy import array, ndarray

from semantic_kernel.connectors.ai.ai_exception import AIException
from semantic_kernel.connectors.ai.ai_service_client_base import AIServiceClientBase
from semantic_kernel.connectors.ai.embeddings.embedding_generator_base import (
    EmbeddingGeneratorBase,
)


class HuggingFaceTextEmbedding(EmbeddingGeneratorBase, AIServiceClientBase):
    device: str
    generator: sentence_transformers.SentenceTransformer

    def __init__(
        self,
        model_id: str,
        device: Optional[int] = -1,
        log: Optional[Logger] = None,
    ) -> None:
        """
        Initializes a new instance of the HuggingFaceTextEmbedding class.

        Arguments:
            model_id {str} -- Hugging Face model card string, see
                https://huggingface.co/sentence-transformers
            device {Optional[int]} -- Device to run the model on, -1 for CPU, 0+ for GPU.
            log {Optional[Logger]} -- Logger instance.

        Note that this model will be downloaded from the Hugging Face model hub.
        """
        resolved_device = (
            f"cuda:{device}" if device >= 0 and torch.cuda.is_available() else "cpu"
        )
        super().__init__(
            model_id=model_id,
            log=log,
            device=resolved_device,
            generator=sentence_transformers.SentenceTransformer(
                model_name_or_path=model_id, device=resolved_device
            ),
        )

    async def generate_embeddings_async(self, texts: List[str]) -> ndarray:
        """
        Generates embeddings for a list of texts.

        Arguments:
            texts {List[str]} -- Texts to generate embeddings for.

        Returns:
            ndarray -- Embeddings for the texts.
        """
        try:
            self.log.info(f"Generating embeddings for {len(texts)} texts")
            embeddings = self.generator.encode(texts)
            return array(embeddings)
        except Exception as e:
            raise AIException("Hugging Face embeddings failed", e)
