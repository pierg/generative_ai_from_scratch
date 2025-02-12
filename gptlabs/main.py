from pathlib import Path
import torch
from gptlabs.utils.torch import save_model_info
from gptlabs.utils.train import generate, train_model
from utils.data import process_data
from gptlabs.models.decoder_v1 import GPT_v1
from gptlabs.models.decoder_v2 import GPT_v2
from gptlabs.models.decoder_v3 import GPT_v3
from gptlabs.models.decoder_v4 import GPT_v4
from gptlabs.models.decoder_v5 import GPT_v5
from gptlabs.models.decoder_v6 import GPT_v6
from gptlabs.models.decoder_v7 import GPT_v7

main_repo = Path(__file__).parent.parent
data_path = main_repo / "input" / 'tiny-shakespeare.txt'
save_folder = main_repo / "output" / "models"

# Hyperparameters for initial and scaled models
hyperparameters_small = { 
    "train_val_split": 0.9,
    "batch_size": 32,
    "max_iters": 3000,
    "block_size": 8,
    "eval_interval": 300,
    "learning_rate": 1e-2,
}

hyperparameters_scaled = { 
    "train_val_split": 0.9,
    "batch_size": 64,
    "block_size": 256,
    "max_iters": 5000,
    "eval_interval": 200,
    "learning_rate": 3e-4,
}

device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Adjust the process_data function call if necessary to accommodate hyperparameters
vocab_size, tokenizer, batch_generator = process_data(data_path, hyperparameters=hyperparameters_small)

dummy_input = torch.zeros((1, 1), dtype=torch.long, device=device)

# Define your models with commentary on what each adds to the previous version.
models = {
    # Basic model with a simple embedding layer, demonstrating the foundational structure.
    "embedding": GPT_v1(vocab_size=vocab_size),
    
    # Adds a linear transformation layer on top of the embeddings, introducing the ability to learn more complex mappings.
    "linear": GPT_v2(vocab_size=vocab_size, n_embd=32),

    # Incorporates positional embeddings, allowing the model to understand sequence order, crucial for text processing.
    "positional": GPT_v3(vocab_size=vocab_size, n_embd=32, block_size=8),

    # Introduces a single head of self-attention, marking the beginning of the model's capacity for contextual understanding.
    "attention": GPT_v4(vocab_size=vocab_size, n_embd=32, block_size=8, head_size=32, dropout=0.1),

    # Expands to multi-head attention, enabling the model to attend to different parts of the sequence simultaneously.
    "multi-attention": GPT_v5(vocab_size=vocab_size, n_embd=32, block_size=8, head_size=8, dropout=0.1, num_heads=4),

    # Add a FeedForward (computation block)
    "computation": GPT_v6(vocab_size=vocab_size, n_embd=32, block_size=8, head_size=8, dropout=0.1, num_heads=4),

    # Adds multiple layers of Transformer blocks, each block includes MultiHeadAttention and FeedForward with residual connections and layer normalization.
    "1_transformer": GPT_v7(vocab_size=vocab_size, n_embd=32, block_size=8, dropout=0.1, num_heads=4, num_layers=3),

    # Transformer architecture scaled up
    "2_t_scaled": GPT_v7(vocab_size=vocab_size, n_embd=384, block_size=256, dropout=0.2, num_heads=6, num_layers=6)
}

def process_model(model_id: str, hyperparameters: dict):
    model = models[model_id]
    model.to(device)
    # Save architecture info
    save_model_info(model, input_tensor=dummy_input, folder=save_folder, id=model_id)
    # Generate text before training
    print(f"Generated text by {model_id} before training:")
    print(generate(model, context=dummy_input, tokenizer=tokenizer))
    # Train the model
    train_model(model, hyperparameters, batch_generator)
    # Generate text after training
    print(f"Generated text by {model_id} after training:")
    print(generate(model, context=dummy_input, tokenizer=tokenizer))

# # Example usage
process_model("1_transformer", hyperparameters_small)

# for model_id in models.keys():
#     print(f"\n\n\n**************\nProcessing model {model_id}")
#     process_model(model_id, hyperparameters_small)
