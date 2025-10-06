#!/usr/bin/env python3
"""
Performance test script for Fourier analysis optimization.
Tests the speed improvement of Phase 1 optimizations.
"""

import time
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scipy.fft import fft, fftfreq
from scipy.stats import chi2

def test_fft_performance():
    """Test FFT performance with different data sizes"""

    print("🧪 Testing Fourier Analysis Performance Improvements")
    print("=" * 60)

    # Test with different data sizes
    test_sizes = [1000, 5000, 10000, 20000]

    for size in test_sizes:
        print(f"\n📊 Testing with {size} data points:")

        # Generate test data (similar to real time series)
        np.random.seed(42)  # For reproducible results
        t = np.linspace(0, 10, size)
        values = np.sin(2 * np.pi * t) + 0.5 * np.random.randn(size)

        # Test OLD method (duplicate FFT + complex significance)
        start_time = time.time()

        # OLD: Duplicate FFT calculations
        fft_values1 = fft(values)
        freqs1 = fftfreq(len(values))
        magnitude1 = np.abs(fft_values1[:len(values)//2])

        fft_values2 = fft(values)  # Duplicate!
        freqs2 = fftfreq(len(values))  # Duplicate!
        magnitude2 = np.abs(fft_values2[:len(values)//2])

        # OLD: Complex chi-squared significance
        frequencies = freqs1[:len(values)//2]
        periods = 1 / frequencies[1:]
        magnitude = magnitude1[1:]

        df = 2
        chi_squared_threshold = chi2.ppf(0.95, df)
        mean_magnitude = np.mean(magnitude)
        scaled_threshold_old = chi_squared_threshold * (mean_magnitude / df)

        old_time = time.time() - start_time

        # Test NEW method (single FFT + simple significance)
        start_time = time.time()

        # NEW: Single FFT calculation
        fft_values = fft(values)
        freqs = fftfreq(len(values))
        magnitude = np.abs(fft_values[:len(values)//2])
        frequencies = freqs[:len(values)//2]

        periods = 1 / frequencies[1:]
        magnitude = magnitude[1:]

        # NEW: Simple percentile significance
        scaled_threshold_new = np.percentile(magnitude, 95)

        new_time = time.time() - start_time

        # Calculate improvement
        speedup = old_time / new_time if new_time > 0 else float('inf')

        print(".3f")
        print(".3f")
        print(".1f")
        print(".3f")
        print(".3f")

        # Verify results are similar
        threshold_diff = abs(scaled_threshold_old - scaled_threshold_new) / scaled_threshold_old * 100
        print(".1f")

if __name__ == "__main__":
    test_fft_performance()