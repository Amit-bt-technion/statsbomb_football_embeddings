from autoencoder import EventAutoencoder
from tokenizer import event_ids
import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from sklearn.preprocessing import OneHotEncoder

torch.backends.cudnn.benchmark = True

# Load the pre-trained autoencoder model
latent_dim = 32
input_dim = 128
autoencoder = EventAutoencoder(input_dim=input_dim, latent_dim=latent_dim)
pretrained_model_path = '../autoencoder/pretrained_autoencoder.pth'
autoencoder.load_state_dict(torch.load(pretrained_model_path, map_location=torch.device('cpu')))

# Disable unecessary gradient calculation for the autoencoder to reduce computations
for param in autoencoder.parameters():
    param.requires_grad = False
autoencoder.eval()
print('Loaded pre-trained autoencoder model.')


# Define a truly lazy-loading Dataset class
class FootballEventDataset(Dataset):
    def __init__(self, csv_root_dir: str, autoencoder, encoder, is_train: bool = True, test_size: float = 0.2,
                 min_id: int = 2, max_id: int = 43, num_of_matches=100):
        self.csv_files = [os.path.join(csv_root_dir, f) for f in os.listdir(csv_root_dir) if f.endswith('.csv')][
                         :num_of_matches]
        self.cache = {}
        self.autoencoder = autoencoder
        self.encoder = encoder
        self.is_train = is_train
        self.test_size = test_size
        self.min_id = min_id
        self.max_id = max_id
        self.indices = []
        self.prepare_data()

    def prepare_data(self):
        total_files = len(self.csv_files)
        split_idx = int(total_files * (1 - self.test_size))
        indices = np.arange(total_files)
        np.random.shuffle(indices)
        self.indices = indices[:split_idx] if self.is_train else indices[split_idx:]

    def __len__(self):
        # Estimate the total length as total rows across selected CSVs
        return len(self.indices) * 1000  # Assuming ~1000 events per CSV

    def __getitem__(self, index):
        # Determine which file and row to access
        file_index = index // 1000  # ~1000 rows per file
        row_index = index % 1000
        file_path = self.csv_files[self.indices[file_index]]

        # Load entire CSV into memory if not already cached
        if file_path not in self.cache:
            print(f"Loading entire CSV: {file_path}")
            df = pd.read_csv(file_path, header=None)
            self.cache[file_path] = df

        # Access the specific row from cached DataFrame
        df = self.cache[file_path]
        row = df.iloc[row_index]

        X = row[2:].values.astype(np.float32).reshape(1, -1)
        y = np.array([[row[1]]])

        y_onehot = self.encoder.transform(y)

        X_tensor = torch.FloatTensor(X)
        y_tensor = torch.FloatTensor(y_onehot)

        # padding the 1st column from which the original event type.id is discarded
        if X_tensor.shape[1] < 128:
            padding = torch.zeros((X_tensor.shape[0], 128 - X_tensor.shape[1]))
            X_tensor = torch.cat((X_tensor, padding), dim=1)

        with torch.no_grad():
            _, X_embedded = self.autoencoder(X_tensor)

        return X_embedded.squeeze(), y_tensor.squeeze()


# Initialize autoencoder and encoder
latent_dim = 32
input_dim = 128
autoencoder = EventAutoencoder(input_dim=input_dim, latent_dim=latent_dim)
encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')

# Valid event types from the event_ids mapping
valid_event_types = list(event_ids.values())
print(f'Valid event types: {valid_event_types}')

# Fit OneHotEncoder only on valid event types
encoder.fit(np.array(valid_event_types).reshape(-1, 1))

# Calculate output dimension based on the OneHotEncoder categories
output_dim = len(encoder.categories_[0])
print(f'Total output classes: {output_dim}')

# Create DataLoader with true lazy loading
batch_size = 2048
train_dataset = FootballEventDataset('../events_csv_targets', autoencoder, encoder, is_train=True, num_of_matches=300)
test_dataset = FootballEventDataset('../events_csv_targets', autoencoder, encoder, is_train=False, num_of_matches=300)
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size)


# Neural Network for Event Type Classification
class EventClassifier(nn.Module):
    def __init__(self, input_dim=32, output_dim=output_dim):
        super(EventClassifier, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, 128),  # Increased neurons
            nn.LeakyReLU(negative_slope=0.01),
            nn.Dropout(0.2),  # Add dropout for regularization
            nn.Linear(128, 128),
            nn.LeakyReLU(negative_slope=0.01),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.LeakyReLU(negative_slope=0.01),
            nn.Linear(64, output_dim),
            nn.Softmax(dim=1)
        )

    def forward(self, x):
        return self.model(x)


class FocalLoss(nn.Module):
    def __init__(self, gamma=2.0, alpha=0.25):
        super(FocalLoss, self).__init__()
        self.gamma = gamma
        self.alpha = alpha
        self.ce = nn.CrossEntropyLoss()

    def forward(self, inputs, targets):
        ce_loss = self.ce(inputs, targets)
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        return focal_loss


# Initialize the model, criterion, and optimizer
model = EventClassifier(input_dim=latent_dim, output_dim=output_dim)
print(next(model.parameters()).device)  # Should print "cuda"
criterion = FocalLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Training loop
num_epochs = 50
for epoch in range(num_epochs):
    model.train()
    total_loss = 0
    for batch_X, batch_y in train_loader:
        optimizer.zero_grad()
        predictions = model(batch_X)
        loss = criterion(predictions, torch.max(batch_y, 1)[1])
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {total_loss / len(train_loader):.4f}")

# Save the trained model to a file
model_path = 'event_classifier.pth'
torch.save(model.state_dict(), model_path)
print(f'Model saved as {model_path}')

# Evaluate the model
model.eval()
correct = 0
total = 0
with torch.no_grad():
    for batch_X, batch_y in test_loader:
        predictions = model(batch_X)
        _, predicted = torch.max(predictions, 1)
        _, actual = torch.max(batch_y, 1)
        correct += (predicted == actual).sum().item()
        total += batch_y.size(0)

accuracy = correct / total
print(f'Test Accuracy: {accuracy * 100:.2f}%')



