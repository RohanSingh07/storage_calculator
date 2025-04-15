from fastapi import FastAPI, Request
# For static files and frontend
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import math
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS (if frontend is served from different origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace * with frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")


# Calculation logic
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
    frame_rate = int(frame_rate.split("fps")[0])
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
    return bit_rate * int(num_cameras) * multiplier

def calculate_storage(num_cameras, bitrate_mbps, hours_per_day, retention_days):
    """
    Calculates total storage (TB) required for recorded video.
    - Converts Mbps → GB/hour → TB total.
    """
    storage_per_hour_GB = (bitrate_mbps * 3600) / (8 * 1024)  
    total_storage_TB = (storage_per_hour_GB * int(hours_per_day) * int(num_cameras) * int(retention_days)) / 1024
    return total_storage_TB


# Route to render index.html
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "Hello from FastAPI"})

@app.post("/submit-camera-data")
async def handle_submit(request: Request):
    form = await request.form()
    data = dict(form)
    print(data)
    # bit_rate = estimate_bit_rate(data["resolution1A"], data["fps1A"], data["compression1A"], data["quality1A"], data["bitrate1A"])
    # total_bandwidth = calculate_bandwidth(bit_rate, data["camera-count1"], data["stream-mode1"])
    # total_storage = calculate_storage(data["camera-count1"], bit_rate, data["recording-hours1A"], data["retention1B"])
    total_bandwidth = 0
    total_storage = 0
    total_bitrate = 0
    
    camera_index = 1
    while f"camera-count{camera_index}" in data:
        prefix = f"{camera_index}"
        
        # Get camera count and stream mode
        num_cameras = int(data[f"camera-count{prefix}"])
        stream_mode = data[f"stream-mode{prefix}"]
        
        # Process stream A
        bit_rate_a = estimate_bit_rate(
            data[f"resolution{prefix}A"],
            data[f"fps{prefix}A"],
            data[f"compression{prefix}A"],
            data[f"quality{prefix}A"],
            data[f"bitrate{prefix}A"]
        )
        
        # Calculate bandwidth for stream A
        bandwidth_a = calculate_bandwidth(bit_rate_a, num_cameras, stream_mode)
        
        # Calculate storage for stream A
        storage_a = calculate_storage(
            num_cameras,
            bit_rate_a,
            data[f"recording-hours{prefix}A"],
            data[f"retention{prefix}A"]
        )
        
        # Add to totals
        total_bandwidth += bandwidth_a
        total_storage += storage_a
        total_bitrate+=bit_rate_a 
        
        # Process stream B if dual mode
        if stream_mode.lower() == "dual":
            bit_rate_b = estimate_bit_rate(
                data[f"resolution{prefix}B"],
                data[f"fps{prefix}B"],
                data[f"compression{prefix}B"],
                data[f"quality{prefix}B"],
                data[f"bitrate{prefix}B"]
            )
            
            # Calculate bandwidth for stream B
            bandwidth_b = calculate_bandwidth(bit_rate_b, num_cameras, stream_mode)
            
            # Calculate storage for stream B
            storage_b = calculate_storage(
                num_cameras,
                bit_rate_b,
                data[f"recording-hours{prefix}B"],
                data[f"retention{prefix}B"]
            )
            
            # Add to totals
            total_bandwidth += bandwidth_b
            total_storage += storage_b
            total_bitrate+=bit_rate_b
        
        camera_index += 1

    return {"message": "Received", "data": {"total_bitrate":total_bitrate, "total_bandwidth":round(total_bandwidth,2), "total_storage":round(total_storage,2)}}


