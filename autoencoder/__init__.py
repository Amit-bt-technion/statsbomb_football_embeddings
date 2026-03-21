import numpy as np
import sys
import pandas as pd
import os
from pathlib import Path
import logging
from tqdm import tqdm
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset, random_split
import pickle
import matplotlib.pyplot as plt
import os


def load_match_events(csv_root_dir: str = os.path.join('..', 'events_csv'), num_of_matches = 3000) -> pd.DataFrame:
    """
    Load all match event CSV files from the specified directory into a single DataFrame.

    Parameters:
    -----------
    csv_root_dir : str
        Path to the root directory containing the CSV files

    Returns:
    --------
    pd.DataFrame
        Combined DataFrame containing all match events
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Convert to Path object for better path handling
    root_path = Path(csv_root_dir)

    # Get list of all CSV files
    csv_files = list(root_path.glob('*.csv'))

    if not csv_files:
        raise ValueError(f"No CSV files found in {csv_root_dir}")

    logger.info(f"Found {len(csv_files)} CSV files to process")

    # Initialize list to store DataFrames
    dfs = []

    # Process each CSV file with progress bar
    for csv_file in tqdm(csv_files[:num_of_matches], desc="Loading CSV files"):
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)

            # Add match_id from filename
            match_id = csv_file.stem.replace('.json', '')
            df['match_id'] = match_id

            dfs.append(df)

        except Exception as e:
            logger.error(f"Error processing {csv_file}: {str(e)}")
            continue

    if not dfs:
        raise ValueError("No valid CSV files were processed")

    # Combine all DataFrames
    logger.info("Combining DataFrames...")
    combined_df = pd.concat(dfs, ignore_index=True)

    logger.info(f"Final DataFrame shape: {combined_df.shape}")

    return combined_df


def plot_losses(train_losses, test_losses):
    """Plot training and test losses."""
    plt.figure(figsize=(10, 6))
    plt.plot(train_losses, label='Train Loss')
    plt.plot(test_losses, label='Test Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Test Losses')
    plt.legend()
    plt.grid(True)
    plt.savefig('loss_plot.png')
    plt.close()


def extract_vectors_from_df(df):
    """Extract vector columns from DataFrame and convert to numpy array."""
    # Get vector columns (assuming they start with 'vector_')
    vector_cols = [col for col in df.columns]

    if not vector_cols:
        raise ValueError("No vector columns found in DataFrame")

    print(f"Found {len(vector_cols)} vector columns")

    # Convert vector columns to numpy array
    vectors = df[vector_cols].values
    return vectors


def prepare_data(df, test_size=0.2):
    """Prepare data for training with train/test split."""
    # Extract vectors from DataFrame
    vectors = extract_vectors_from_df(df)

    # Convert to tensor
    X_tensor = torch.FloatTensor(vectors)

    # Create dataset
    dataset = TensorDataset(X_tensor, X_tensor)

    # Calculate split sizes
    test_size = int(len(dataset) * test_size)
    train_size = len(dataset) - test_size

    # Split dataset
    train_dataset, test_dataset = random_split(dataset, [train_size, test_size])

    return X_tensor, train_dataset, test_dataset


class EventAutoencoder(nn.Module):
    def __init__(self, input_dim=128, latent_dim=32):
        super(EventAutoencoder, self).__init__()

        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, input_dim),
            nn.ReLU(),
            nn.Linear(input_dim, input_dim),
            nn.ReLU(),
            nn.Linear(input_dim, input_dim),
            nn.ReLU(),
            nn.Linear(input_dim, input_dim),
            nn.ReLU(),
            nn.Linear(input_dim, latent_dim)
        )

        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, input_dim),
            nn.ReLU(),
            nn.Linear(input_dim, input_dim),
            nn.ReLU(),
            nn.Linear(input_dim, input_dim),
            nn.ReLU(),
            nn.Linear(input_dim, input_dim),
            nn.ReLU(),
            nn.Linear(input_dim, input_dim)
        )

    def forward(self, x):
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed, latent

    def encode(self, x):
        return self.encoder(x)


def train_model(train_loader, model, test_loader=None, num_epochs=100, learning_rate=0.001, criterion=nn.MSELoss()):
    """Train the autoencoder with validation."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    # criterion = nn.L1Loss()

    print(f"Training on {device}")

    train_losses = []
    test_losses = []

    for epoch in range(num_epochs):
        model.train()
        total_loss = 0

        # Training loop
        for batch_features, _ in tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs}", leave=False):
            batch_features = batch_features.to(device)

            # Forward pass
            reconstructed, _ = model(batch_features)

            # Compute loss
            loss = criterion(reconstructed, batch_features)

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_train_loss = total_loss / len(train_loader)
        train_losses.append(avg_train_loss)

        # Validation loop
        if test_loader is not None:
            model.eval()
            total_test_loss = 0
            with torch.no_grad():
                for batch_features, _ in test_loader:
                    batch_features = batch_features.to(device)
                    reconstructed, _ = model(batch_features)
                    loss = criterion(reconstructed, batch_features)
                    total_test_loss += loss.item()

            avg_test_loss = total_test_loss / len(test_loader)
            test_losses.append(avg_test_loss)

            print(f'Epoch [{epoch+1}/{num_epochs}], Train Loss: {avg_train_loss:.6f}, Test Loss: {avg_test_loss:.6f}')
        else:
            print(f'Epoch [{epoch+1}/{num_epochs}], Train Loss: {avg_train_loss:.6f}')

    # Plot losses
    if test_loader is not None:
        plot_losses(train_losses, test_losses)

    return model


def get_embeddings(model, data_loader):
    """Generate embeddings for all events."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()

    embeddings = []

    with torch.no_grad():
        for batch in tqdm(data_loader, desc="Generating embeddings"):
            batch = batch[0].to(device)  # batch is a tuple (input, target), we need only input
            latent = model.encode(batch)
            embeddings.append(latent.cpu().numpy())
    return np.vstack(embeddings)

if __name__ == "__main__":
    df = pd.read_csv('../zipped/15956.json.csv', engine='python')
    print(df.shape)
    df.drop(['Unnamed: 0'], axis=1, inplace=True)
    # df.drop(['match_id'], axis=1, inplace=True)
    print(df.columns)

    try:
        df = load_match_events(num_of_matches=1500)
        print(f"Successfully loaded {len(df)} events from all matches")

        # Display some basic statistics
        print("\nDataset Statistics:")
        print(f"Total number of matches: {df['match_id'].nunique()}")
        print(f"Memory usage: {df.memory_usage().sum() / 1024**2:.2f} MB")

    except Exception as e:
        print(f"Error: {str(e)}")


    batch_size = 64
    num_epochs = 10
    latent_dim = 32

    # Prepare data with train/test split
    print("Preparing data...")
    X_tensor, train_dataset, test_dataset = prepare_data(df)

    # Extract embeddings first column
    # Get indices of the test dataset
    test_indices = test_dataset.indices

    # Get the original tensor data for these indices
    test_data = X_tensor[test_indices]

    # Extract the first column
    embeddings_event_types = test_data[:, 0]

    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)

    # Initialize model
    print("Initializing model...")
    input_dim = len([col for col in df.columns])
    model_l1 = EventAutoencoder(input_dim=input_dim, latent_dim=latent_dim)
    model_mse = EventAutoencoder(input_dim=input_dim, latent_dim=latent_dim)

    # Train model
    print("Training with MSE criterion")
    model_mse = train_model(train_loader, model_mse, test_loader, num_epochs=num_epochs, criterion=nn.MSELoss())

    # Generate embeddings
    print("Generating embeddings...")
    embeddings_mse = get_embeddings(model_mse, test_loader)

    # Save results
    print("Saving results...")
    results = {
        'embeddings_mse': embeddings_mse,
        'model_state': model_mse.state_dict()
    }

    # Specify the file path for saving the model
    model_save_path = 'model_mse.pth'

    # Save the trained model's state_dict
    torch.save(model_mse.state_dict(), model_save_path)
    print(f"Model saved to {model_save_path}")

    print("Pipeline complete!")
