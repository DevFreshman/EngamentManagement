import torch
import torch.nn as nn


class SimpleCNN(nn.Module):
    def make_block(self, in_channels, out_channels):
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=1, padding="same"),
            nn.BatchNorm2d(out_channels),
            nn.LeakyReLU(),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding="same"),
            nn.BatchNorm2d(out_channels),
            nn.LeakyReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

    def __init__(self, num_class=6):
        super().__init__()
        self.conv1 = self.make_block(3, 8)
        self.conv2 = self.make_block(8, 16)
        self.conv3 = self.make_block(16, 32)
        self.conv4 = self.make_block(32, 64)
        self.conv5 = self.make_block(64, 128)

        self.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(6272, 512),
            nn.LeakyReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 1024),
            nn.LeakyReLU(),
            nn.Dropout(0.5),
            nn.Linear(1024, num_class),
        )

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        x = self.conv5(x)
        x = x.view(x.shape[0], -1)
        return self.fc(x)
