import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from sklearn import metrics
import tensorflow as tf

# Seaborn options
sns.set(style="whitegrid", font_scale=1.4)


def plot_training_curves(history, figsize=(12, 5)):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    ax1.plot(history.history['accuracy'])
    ax1.plot(history.history['val_accuracy'])
    ax1.set_title('Model accuracy')
    ax1.set_ylabel('Accuracy')
    ax1.set_xlabel('Epoch')
    ax1.legend(['Train', 'Val'], loc='upper left')

    ax2.plot(history.history['loss'])
    ax2.plot(history.history['val_loss'])
    ax2.set_title('Model loss')
    ax2.set_ylabel('Loss')
    ax2.set_xlabel('Epoch')
    ax2.legend(['Train', 'Val'], loc='upper left')

    return fig


def accuracy_vs_train_size(model, initial_weights, X_train, y_train,
                           X_val, y_val, X_test, y_test, sizes):
    test_accuracies = []
    for size in sizes:
        # Defines early stopper
        early_stopper = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss', mode='auto', patience=2,
            verbose=1, restore_best_weights=True
        )
        # Reset weights to initial value
        model.set_weights(initial_weights)

        # Train model on data subset
        model.fit(
            X_train[:size], y_train[:size],
            validation_data=(X_val, y_val),
            epochs=30, batch_size=32,
            callbacks=[early_stopper], verbose=2
        )

        # Evaluate on test set
        probas = model.predict(X_test)
        y_pred = (probas > 0.5).astype(np.int)
        test_acc = metrics.accuracy_score(y_test, y_pred)
        test_accuracies.append(test_acc)

    return test_accuracies
