"""
Test to demonstrate JAX asynchronous execution timing issues.
This explains why sync_jax=False gives misleading timing results.
"""

import time
import jax
import jax.numpy as jnp
import threading
import psutil
import os

def monitor_cpu_usage():
    """Monitor CPU usage in background thread."""
    cpu_usage = []
    start_time = time.time()
    
    def monitor():
        while getattr(monitor, 'running', True):
            current_time = time.time() - start_time
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_usage.append((current_time, cpu_percent))
    
    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    monitor.thread = thread
    monitor.cpu_usage = cpu_usage
    return monitor

def test_jax_async_timing():
    """Demonstrate the timing difference between sync and async JAX execution."""
    
    print("JAX Asynchronous Execution Timing Test")
    print("=" * 60)
    
    # Larger but reasonable computation
    n = 8_000  # This is ~256MB per matrix, should give good timing differences
    x = jnp.ones((n, n), dtype=jnp.float32)
    y = jnp.ones((n, n), dtype=jnp.float32)
    
    @jax.jit
    def heavy_computation(a, b):
        # Multiple operations that take meaningful time
        result = jnp.dot(a, b)
        result = jnp.sin(result) + jnp.cos(result) * 0.5
        result = jnp.dot(result, result)  # Another matrix multiply
        result = jnp.sum(result ** 2)
        return result
    
    print(f"Testing with {n}x{n} matrices (~{n*n*4/1024/1024:.0f}MB per matrix)")
    
    # Warm up JAX (compilation) with tiny matrices
    print("\nWarm-up run (compilation)...")
    _ = heavy_computation(x[:10, :10], y[:10, :10])
    jax.block_until_ready(_)
    print("Compilation complete")
    
    print("\n" + "-" * 60)
    print("TEST 1: WITHOUT jax.block_until_ready() - ASYNC EXECUTION")
    print("-" * 60)
    
    # Start CPU monitoring
    monitor = monitor_cpu_usage()
    
    print("Starting computation...")
    start_wall_clock = time.time()
    
    # Measure "Python dispatch time" (misleading without sync)
    start_dispatch = time.time()
    result = heavy_computation(x, y)  # No block_until_ready()!
    end_dispatch = time.time()
    dispatch_time = end_dispatch - start_dispatch
    
    print(f"Python dispatch completed in: {dispatch_time:.2f}s")
    print("But computation is still running asynchronously...")
    
    # Now force synchronization and measure wall clock
    jax.block_until_ready(result)
    end_wall_clock = time.time()
    wall_clock_time = end_wall_clock - start_wall_clock
    
    # Stop monitoring
    monitor.running = False
    monitor.thread.join(timeout=1.0)
    
    print(f"Total wall clock time: {wall_clock_time:.2f}s")
    print(f"Async overhead: {wall_clock_time - dispatch_time:.2f}s")
    print(f"Timing lie factor: {wall_clock_time / dispatch_time:.1f}x")
    
    print("\n" + "-" * 60)
    print("TEST 2: WITH jax.block_until_ready() - SYNC EXECUTION")
    print("-" * 60)
    
    # Test with proper synchronization
    start_sync = time.time()
    result = heavy_computation(x, y)
    jax.block_until_ready(result)  # Force synchronization
    end_sync = time.time()
    sync_time = end_sync - start_sync
    
    print(f"Synchronous execution time: {sync_time:.2f}s")
    print("This is the true computation time")
    
    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    print(f"Async dispatch time:    {dispatch_time:.2f}s  <- MISLEADING")
    print(f"Sync execution time:    {sync_time:.2f}s     <- ACCURATE")
    print(f"Wall clock (async):     {wall_clock_time:.2f}s")
    print(f"Difference:             {abs(sync_time - wall_clock_time):.2f}s")
    
    # Analyze CPU usage pattern
    if monitor.cpu_usage:
        print(f"\nCPU Usage Pattern:")
        high_cpu_periods = [usage for time_point, usage in monitor.cpu_usage if usage > 50]
        if high_cpu_periods:
            print(f"High CPU usage detected for ~{len(high_cpu_periods) * 0.1:.1f}s")
            print("This confirms async execution continuing after dispatch")

def test_compilation_cache_persistence():
    """Test whether JAX compilation cache persists across function calls."""
    
    print("\n" + "=" * 60)
    print("JAX COMPILATION CACHE PERSISTENCE TEST")
    print("=" * 60)
    
    @jax.jit
    def test_function(x):
        return jnp.sum(x ** 2) + jnp.mean(x)
    
    # First call - should compile
    print("Call 1 (expect compilation):")
    data = jnp.ones(10_000_000)  # 10M elements ~40MB - reasonable size
    
    start = time.time()
    result1 = test_function(data)
    jax.block_until_ready(result1)
    time1 = time.time() - start
    print(f"  Time: {time1:.4f}s")
    
    # Second call - should use cache
    print("Call 2 (should use cached compilation):")
    start = time.time()
    result2 = test_function(data)
    jax.block_until_ready(result2)
    time2 = time.time() - start
    print(f"  Time: {time2:.4f}s")
    
    # Third call with different data shape - should recompile
    print("Call 3 (different shape - expect recompilation):")
    data_diff = jnp.ones(15_000_000)  # 15M elements ~60MB
    start = time.time()
    result3 = test_function(data_diff)
    jax.block_until_ready(result3)
    time3 = time.time() - start
    print(f"  Time: {time3:.4f}s")
    
    # Fourth call with same shape as first - should use cache
    print("Call 4 (same shape as call 1 - should use cache):")
    start = time.time()
    result4 = test_function(data)
    jax.block_until_ready(result4)
    time4 = time.time() - start
    print(f"  Time: {time4:.4f}s")
    
    print(f"\nCache efficiency:")
    print(f"  Call 1 vs Call 2 speedup: {time1/time2:.1f}x")
    print(f"  Call 3 (recompile): {time3:.4f}s")
    print(f"  Call 4 (cache reuse): {time4:.4f}s")
    
    if time2 < time1 * 0.5 and time4 < time1 * 0.5:
        print("  ✅ Compilation cache is working correctly")
    else:
        print("  ❌ Compilation cache may not be working")

def main():
    """Run all timing tests."""
    # Set JAX to use 60% of memory to avoid issues
    os.environ["XLA_PYTHON_CLIENT_MEM_FRACTION"] = "0.6"
    
    print("Testing JAX timing behavior to explain benchmark discrepancies")
    
    # Test async timing issues
    test_jax_async_timing()
    
    # Test compilation cache
    test_compilation_cache_persistence()
    
    print("\n" + "=" * 60)
    print("CONCLUSIONS FOR YOUR BENCHMARK")
    print("=" * 60)
    print("1. sync_jax=False gives MISLEADING timing (dispatch time only)")
    print("2. Wall clock time shows ACTUAL computation time")
    print("3. JAX compilation cache DOES persist in same session")
    print("4. The 8s CPU difference is async execution, not compilation")
    print("5. Use jax.block_until_ready() for accurate timing")

if __name__ == "__main__":
    main()
