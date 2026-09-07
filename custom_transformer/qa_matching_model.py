import torch
import torch.nn as nn
from custom_transformer import layers
from custom_transformer.my_embeddings import MyQAMatchingTransformerEmbeddings
from RuntimeSettings import load_runtime_settings

settings = load_runtime_settings()



class QAMatchingTransformer(nn.Module):
    def __init__(self, hidden_dim, vocab_size, max_position_embeddings, num_heads, num_blocks, num_labels=1):
        super().__init__()

        self.dropout = nn.Dropout(0.1)

        self.embeddings = MyQAMatchingTransformerEmbeddings(
            vocab_size=vocab_size,
            hidden_dim=hidden_dim,
            max_position_embeddings=max_position_embeddings
        )

        self.blocks = nn.ModuleList(
            [
                layers.EncoderLayer(
                    d_model=hidden_dim,
                    num_heads=num_heads,
                    d_ff=hidden_dim * settings["num_heads_to_predict"],
                    dropout=settings["dropout"]
                )
                for _ in range(num_blocks)
            ]
        )

        self.ln_f = nn.LayerNorm(hidden_dim)
        self.classifier = nn.Linear(hidden_dim, num_labels)

    def forward(self, x, mask=None, token_weights=None, return_score=False):
        x = self.embeddings(x, token_weights)

        if mask is not None:
            mask = mask.unsqueeze(1).unsqueeze(2)

        for block in self.blocks:
            x = block(x, mask)

        x = self.ln_f(x)

        pooled_output = x[:, 0]
        pooled_output = self.dropout(pooled_output)

        match_logits = self.classifier(pooled_output)

        if return_score:
            return torch.sigmoid(match_logits)

        return match_logits