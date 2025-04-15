import math

def get_resolution_pixels(resolution):
    """
    Convert resolution string (e.g., '1920x1080') to total pixels.
    Defaults to 1080p (1920x1080) if invalid.
    """
    try:
        width, height = map(int, resolution.lower().split('x'))
        if width <= 0 or height <= 0:
            raise ValueError
        return width * height
    except:
        print("Invalid resolution format! Defaulting to 1920x1080.")
        return 1920 * 1080

def estimate_bit_rate(resolution, frame_rate, compression, quality, bitrate_mode='CBR'):
    """
    Estimates bitrate (Mbps) based on:
    - Resolution (e.g., '3840x2160')
    - Frame rate (fps)
    - Compression codec (H.264, H.265, etc.)
    - Quality (low, medium, good, etc.)
    - Bitrate mode (CBR or VBR).
    """
    # Resolution in megapixels
    resolution_pixels = get_resolution_pixels(resolution) / 1e6  

    # Needs to be fine tuned according to the expected results
    quality_factors = {
        "low": 0.03,
        "medium": 0.045,
        "good": 0.065,
        "high": 0.08,
        "excellent": 0.15
    }
    bit_depth = quality_factors.get(quality.lower()) 

    # Codec efficiency (higher = better compression) Needs to be fine tuned according to the expected results
    codec_efficiency = {
        'mpeg-4': 1.0,# can be removed
        'h.264': 1.5,
        'h.265': 2.0,
        'av1': 2.5 # can be removed
    }
    efficiency = codec_efficiency.get(compression.lower(), 1.0)  # Default: Mpeg-4

    # Base bitrate (Mbps)
    bit_rate = (resolution_pixels * frame_rate * bit_depth) / efficiency

    # Adjust for VBR (Variable Bitrate)
    if bitrate_mode.upper() == 'VBR':
        bit_rate *= 0.7  # VBR typically uses 70-75% of CBR

    return bit_rate

def calculate_bandwidth(bit_rate, num_cameras, stream_mode='single'):
    """
    Calculates total bandwidth (Mbps) for multiple cameras.
    - `stream_mode`: 'single' (1 stream) or 'dual' (2 streams per camera).
    """
    multiplier = 2 if stream_mode.lower() == 'dual' else 1
    return bit_rate * num_cameras * multiplier

def calculate_storage(num_cameras, bitrate_mbps, hours_per_day, retention_days):
    """
    Calculates total storage (TB) required for recorded video.
    - Converts Mbps → GB/hour → TB total.
    """
    storage_per_hour_GB = (bitrate_mbps * 3600) / (8 * 1024)  
    total_storage_TB = (storage_per_hour_GB * hours_per_day * num_cameras * retention_days) / 1024
    return total_storage_TB

def main():
    print("\n=== Video Surveillance Bitrate Calculator ===")
    
    # User inputs
    num_cameras = int(input("Enter number of cameras: "))
    stream_mode = input("Enter stream mode [single/dual]: ").strip()
    resolution = input("Enter resolution (e.g., 1920x1080, 3840x2160): ").strip()
    frame_rate = float(input("Enter frame rate (fps): "))
    print("\nSupported codecs: Mpeg-4 (low efficiency), H.264 (medium), H.265 (high), AV1 (best)")
    compression = input("Enter compression type: ").strip()
    print("\nQuality levels: low, medium, good, high, excellent")
    quality = input("Enter video quality: ").strip()
    bitrate_mode = input("Enter bitrate mode [CBR/VBR]: ").strip()
    recording_hours = float(input("Enter recording hours per day: "))
    retention_days = int(input("Enter retention period (days): "))

    # Live preview (optional)
    live_preview = input("\nEnable live preview? [yes/no]: ").strip().lower()
    if live_preview == 'yes':
        live_cameras = int(input("Enter number of live preview cameras: "))
        live_stream_mode = input("Enter live stream mode [single/dual]: ").strip()
        live_resolution = input("Enter live resolution (e.g., 1280x720): ").strip()
        live_fps = float(input("Enter live frame rate (fps): "))
        live_compression = input("Enter live compression type: ").strip()
        live_quality = input("Enter live quality [low/medium/good]: ").strip()
        live_bitrate = estimate_bit_rate(live_resolution, live_fps, live_compression, live_quality)
        live_bandwidth = calculate_bandwidth(live_bitrate, live_cameras, live_stream_mode)
        print(f"\nLive Preview Bandwidth: {live_bandwidth:.2f} Mbps")

    # Calculations
    bit_rate = estimate_bit_rate(resolution, frame_rate, compression, quality, bitrate_mode)
    total_bandwidth = calculate_bandwidth(bit_rate, num_cameras, stream_mode)
    total_storage = calculate_storage(num_cameras, bit_rate, recording_hours, retention_days)

    # Results
    print("\n=== Results ===")
    print(f"Bitrate per Camera: {bit_rate:.2f} Mbps ({bitrate_mode.upper()})")
    print(f"Total Bandwidth: {total_bandwidth:.2f} Mbps")
    print(f"Total Storage Required: {total_storage:.2f} TB")

if __name__ == "__main__":
    main()