import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.datasets as datasets
from torch.utils.data import DataLoader
from torchvision import transforms

class Discriminator(nn.Module):
    def __init__(self, img_dim):
        super().__init__()
        self.disc = nn.Sequential(
            nn.Linear(img_dim, 512),
            nn.BatchNorm1d(512),
            nn.LeakyReLU(0.1),
            nn.Linear(512, 128),
            nn.BatchNorm1d(128),
            nn.LeakyReLU(0.1),
            nn.Linear(128, 1),
            nn.Sigmoid(),
        )
    
    def forward(self, x):
        return self.disc(x)
    
class Generator(nn.Module):
    def __init__(self, z_dim, img_dim):
        super().__init__()
        self.gen = nn.Sequential(
            nn.Linear(z_dim, 256),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.1),
            nn.Linear(256, 512),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.1),
            nn.Linear(512, img_dim),
            nn.BatchNorm2d(img_dim),
            nn.Tanh(),
        )

    def forward(self, x):
        return self.gen(x)
    

# hyperparameters config
device = "cuda" if torch.cuda.is_available() else "cpu"
lr = 3e-4
z_dim = 64
image_dim = 28 * 28 * 1 # 784
batch_size = 32
num_epochs = 50

disc = Discriminator(image_dim).to(device)
gen = Generator(z_dim, image_dim).to(device)
fixed_noise = torch.randn(batch_size, z_dim).to(device) # noise generation
transforms = transforms.Compose(
    [transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))]
)
dataset = datasets.MNIST(root="dataset/", transform=transforms, download=True)
loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
opt_disc = optim.Adam(disc.parameters(), lr=lr)
opt_gen = optim.Adam(gen.parameters(), lr=lr)
criterion = nn.BCELoss()
step = 0

gen_train_loss, disc_train_loss = 0.0, 0.0

for epoch in range(num_epochs):
    for batch_idx, (real, _) in enumerate(loader):
        real = real.view(-1, 784).to(device)
        batch_size = real.shape[0]

        # train discriminator
        noise = fixed_noise
        fake = gen(noise)
        disc_real = disc(real).view(-1)
        lossD_real = criterion(disc_real, torch.ones_like(disc_real))
        disc_fake = disc(fake.detach()).view(-1)
        lossD_fake = criterion(disc_fake, torch.zeros_like(disc_fake))
        lossD = (lossD_real + lossD_fake) / 2
        disc_train_loss += lossD
        disc.zero_grad()
        lossD.backward()
        opt_disc.step()

        # train generator
        disc_output = disc(fake).view(-1)
        lossG = criterion(disc_output, torch.ones_like(disc_output))
        gen_train_loss += lossG
        gen.zero_grad()
        lossG.backward()
        opt_gen.step()

        print(f"Epoch: {epoch}\nGenerator Training Loss: {gen_train_loss:.4f}, Discriminator Training loss: {disc_train_loss:.4f}")




