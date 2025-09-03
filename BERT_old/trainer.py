"""
BERT Training Engine
"""

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import get_linear_schedule_with_warmup
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging
from tqdm import tqdm
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class BERTTrainer:
    """BERT training engine"""
    
    def __init__(self, model, config, device):
        self.model = model
        self.config = config
        self.device = device
        self.model.to(device)
        
        # Training components
        self.optimizer = AdamW(
            model.parameters(),
            lr=config.LEARNING_RATE,
            weight_decay=config.WEIGHT_DECAY
        )
        
        # Metrics tracking
        self.train_losses = []
        self.val_losses = []
        self.train_accuracies = []
        self.val_accuracies = []
        
        # Create output directory
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        
        logger.info(f"🚀 Initialized BERT trainer on device: {device}")
    
    def train_epoch(self, train_loader):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        correct_predictions = 0
        total_predictions = 0
        
        progress_bar = tqdm(train_loader, desc="Training")
        
        for batch in progress_bar:
            # Move batch to device
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            labels = batch['labels'].to(self.device)
            
            # Forward pass
            loss, logits = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.MAX_GRAD_NORM)
            
            # Optimizer step
            self.optimizer.step()
            self.optimizer.zero_grad()
            
            # Metrics
            total_loss += loss.item()
            predictions = torch.argmax(logits, dim=1)
            correct_predictions += (predictions == labels).sum().item()
            total_predictions += labels.size(0)
            
            # Update progress bar
            progress_bar.set_postfix({
                'Loss': f'{loss.item():.4f}',
                'Acc': f'{100 * correct_predictions / total_predictions:.2f}%'
            })
        
        avg_loss = total_loss / len(train_loader)
        accuracy = correct_predictions / total_predictions
        
        return avg_loss, accuracy
    
    def evaluate(self, val_loader):
        """Evaluate model on validation set"""
        self.model.eval()
        total_loss = 0
        correct_predictions = 0
        total_predictions = 0
        all_predictions = []
        all_labels = []
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Evaluating"):
                # Move batch to device
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                # Forward pass
                loss, logits = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                # Metrics
                total_loss += loss.item()
                predictions = torch.argmax(logits, dim=1)
                correct_predictions += (predictions == labels).sum().item()
                total_predictions += labels.size(0)
                
                # Store predictions and labels
                all_predictions.extend(predictions.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        avg_loss = total_loss / len(val_loader)
        accuracy = correct_predictions / total_predictions
        
        return avg_loss, accuracy, all_predictions, all_labels
    
    def train(self, train_loader, val_loader, num_epochs):
        """Main training loop"""
        logger.info(f"🎯 Starting training for {num_epochs} epochs...")
        
        # Learning rate scheduler
        total_steps = len(train_loader) * num_epochs
        scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=self.config.WARMUP_STEPS,
            num_training_steps=total_steps
        )
        
        best_val_accuracy = 0
        
        for epoch in range(num_epochs):
            logger.info(f"\n📚 Epoch {epoch + 1}/{num_epochs}")
            
            # Training
            train_loss, train_acc = self.train_epoch(train_loader)
            
            # Validation
            val_loss, val_acc, val_preds, val_labels = self.evaluate(val_loader)
            
            # Store metrics
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            self.train_accuracies.append(train_acc)
            self.val_accuracies.append(val_acc)
            
            # Log results
            logger.info(f"📊 Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
            logger.info(f"📊 Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
            
            # Save best model
            if val_acc > best_val_accuracy:
                best_val_accuracy = val_acc
                self.save_model(f"{self.config.OUTPUT_DIR}/best_model.pt")
                logger.info(f"💾 New best model saved! Val Acc: {val_acc:.4f}")
            
            # Save checkpoint
            if (epoch + 1) % 2 == 0:
                self.save_checkpoint(epoch, f"{self.config.OUTPUT_DIR}/checkpoint_epoch_{epoch+1}.pt")
            
            # Update learning rate
            scheduler.step()
        
        logger.info("🎉 Training complete!")
        self.plot_training_curves()
        self.save_training_history()
    
    def save_model(self, path):
        """Save model"""
        torch.save(self.model.state_dict(), path)
        logger.info(f"💾 Model saved to {path}")
    
    def save_checkpoint(self, epoch, path):
        """Save training checkpoint"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'train_accuracies': self.train_accuracies,
            'val_accuracies': self.val_accuracies
        }
        torch.save(checkpoint, path)
        logger.info(f"💾 Checkpoint saved to {path}")
    
    def plot_training_curves(self):
        """Plot training curves"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Loss curves
        ax1.plot(self.train_losses, label='Train Loss')
        ax1.plot(self.val_losses, label='Val Loss')
        ax1.set_title('Training and Validation Loss')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.legend()
        ax1.grid(True)
        
        # Accuracy curves
        ax2.plot(self.train_accuracies, label='Train Accuracy')
        ax2.plot(self.val_accuracies, label='Val Accuracy')
        ax2.set_title('Training and Validation Accuracy')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig(f"{self.config.OUTPUT_DIR}/training_curves.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        logger.info(f"📈 Training curves saved to {self.config.OUTPUT_DIR}/training_curves.png")
    
    def save_training_history(self):
        """Save training history"""
        history = {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'train_accuracies': self.train_accuracies,
            'val_accuracies': self.val_accuracies,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(f"{self.config.OUTPUT_DIR}/training_history.json", 'w') as f:
            json.dump(history, f, indent=2)
        
        logger.info(f"📊 Training history saved to {self.config.OUTPUT_DIR}/training_history.json")
