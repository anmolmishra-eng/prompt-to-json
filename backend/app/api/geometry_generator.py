"""
GLB Geometry Generation API
Generates 3D geometry files from design specifications
"""

import json
import logging
import os
import struct
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/geometry", tags=["Geometry Generation"])


class GeometryRequest(BaseModel):
    """Geometry generation request"""

    spec_json: Dict[str, Any] = Field(..., description="Design specification")
    request_id: str = Field(..., description="Request identifier")
    format: str = Field(default="glb", description="Output format (glb, obj)")


class GeometryResponse(BaseModel):
    """Geometry generation response"""

    request_id: str
    geometry_url: str
    format: str
    file_size_bytes: int
    generation_time_ms: int


class GLBGenerator:
    """Generate GLB files from design specifications"""

    def __init__(self, output_dir: str = "data/geometry_outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_glb(self, spec_json: Dict[str, Any], request_id: str) -> str:
        """Generate GLB file from design specification"""

        try:
            # Create simple GLB with basic room geometry
            glb_content = self._create_simple_glb(spec_json)

            # Save GLB file
            glb_filename = f"{request_id}.glb"
            glb_path = os.path.join(self.output_dir, glb_filename)

            with open(glb_path, "wb") as f:
                f.write(glb_content)

            logger.info(f"Generated GLB file: {glb_path}")
            return glb_path

        except Exception as e:
            logger.error(f"GLB generation failed for {request_id}: {e}")
            raise

    def _create_simple_glb(self, spec_json: Dict[str, Any]) -> bytes:
        """Create simple GLB with basic room geometry"""

        # Extract room dimensions
        rooms = spec_json.get("rooms", [])
        if not rooms:
            rooms = [{"type": "room", "length": 4.0, "width": 4.0, "height": 3.0}]

        room = rooms[0]
        length = room.get("length", 4.0)
        width = room.get("width", 4.0)
        height = room.get("height", 3.0)

        # Create simple box geometry
        vertices = [
            # Floor vertices
            0.0,
            0.0,
            0.0,  # 0
            length,
            0.0,
            0.0,  # 1
            length,
            width,
            0.0,  # 2
            0.0,
            width,
            0.0,  # 3
            # Ceiling vertices
            0.0,
            0.0,
            height,  # 4
            length,
            0.0,
            height,  # 5
            length,
            width,
            height,  # 6
            0.0,
            width,
            height,  # 7
        ]

        # Indices for box faces
        indices = [
            # Floor
            0,
            1,
            2,
            0,
            2,
            3,
            # Ceiling
            4,
            7,
            6,
            4,
            6,
            5,
            # Walls
            0,
            4,
            5,
            0,
            5,
            1,  # Front
            2,
            6,
            7,
            2,
            7,
            3,  # Back
            0,
            3,
            7,
            0,
            7,
            4,  # Left
            1,
            5,
            6,
            1,
            6,
            2,  # Right
        ]

        # Convert to bytes
        vertex_bytes = bytearray()
        for v in vertices:
            vertex_bytes += struct.pack("<f", v)

        index_bytes = bytearray()
        for i in indices:
            index_bytes += struct.pack("<H", i)

        # Pad to 4-byte boundary
        while len(vertex_bytes) % 4 != 0:
            vertex_bytes += b"\x00"
        while len(index_bytes) % 4 != 0:
            index_bytes += b"\x00"

        binary_data = vertex_bytes + index_bytes

        # Create glTF JSON
        gltf_json = {
            "asset": {"version": "2.0", "generator": "BHIV GLB Generator"},
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [{"mesh": 0}],
            "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 1, "material": 0}]}],
            "materials": [
                {
                    "name": "RoomMaterial",
                    "pbrMetallicRoughness": {
                        "baseColorFactor": [0.8, 0.8, 0.8, 1.0],
                        "metallicFactor": 0.0,
                        "roughnessFactor": 0.8,
                    },
                }
            ],
            "accessors": [
                {
                    "bufferView": 0,
                    "componentType": 5126,  # FLOAT
                    "count": 8,
                    "type": "VEC3",
                    "min": [0.0, 0.0, 0.0],
                    "max": [length, width, height],
                },
                {"bufferView": 1, "componentType": 5123, "count": len(indices), "type": "SCALAR"},  # UNSIGNED_SHORT
            ],
            "bufferViews": [
                {"buffer": 0, "byteOffset": 0, "byteLength": len(vertex_bytes)},
                {"buffer": 0, "byteOffset": len(vertex_bytes), "byteLength": len(index_bytes)},
            ],
            "buffers": [{"byteLength": len(binary_data)}],
        }

        # Convert JSON to bytes
        json_bytes = json.dumps(gltf_json, separators=(",", ":")).encode("utf-8")

        # Pad JSON to 4-byte boundary
        while len(json_bytes) % 4 != 0:
            json_bytes += b" "

        # Create GLB
        total_length = 12 + 8 + len(json_bytes) + 8 + len(binary_data)

        glb_header = struct.pack("<III", 0x46546C67, 2, total_length)
        json_chunk = struct.pack("<II", len(json_bytes), 0x4E4F534A) + json_bytes
        bin_chunk = struct.pack("<II", len(binary_data), 0x004E4942) + binary_data

        return glb_header + json_chunk + bin_chunk


# Global instance
glb_generator = GLBGenerator()


@router.post("/generate", response_model=GeometryResponse)
async def generate_geometry(request: GeometryRequest, background_tasks: BackgroundTasks):
    """Generate 3D geometry file from design specification"""

    start_time = datetime.now()

    try:
        if request.format.lower() == "glb":
            geometry_path = glb_generator.generate_glb(request.spec_json, request.request_id)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")

        # Get file size
        file_size = os.path.getsize(geometry_path)

        # Calculate generation time
        generation_time = int((datetime.now() - start_time).total_seconds() * 1000)

        # Generate URL
        geometry_url = f"/api/v1/geometry/download/{request.request_id}.{request.format}"

        logger.info(f"Geometry generated: {geometry_path} ({file_size} bytes)")

        return GeometryResponse(
            request_id=request.request_id,
            geometry_url=geometry_url,
            format=request.format,
            file_size_bytes=file_size,
            generation_time_ms=generation_time,
        )

    except Exception as e:
        logger.error(f"Geometry generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Geometry generation failed: {str(e)}")


@router.get("/download/{filename}")
async def download_geometry(filename: str):
    """Download generated geometry file"""

    file_path = os.path.join(glb_generator.output_dir, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Geometry file not found")

    from fastapi.responses import FileResponse

    return FileResponse(
        file_path,
        media_type="model/gltf-binary" if filename.endswith(".glb") else "application/octet-stream",
        filename=filename,
    )


@router.get("/list")
async def list_geometry_files():
    """List all generated geometry files"""

    files = []
    if os.path.exists(glb_generator.output_dir):
        for filename in os.listdir(glb_generator.output_dir):
            if filename.endswith((".glb", ".obj")):
                file_path = os.path.join(glb_generator.output_dir, filename)
                file_stat = os.stat(file_path)

                files.append(
                    {
                        "filename": filename,
                        "size_bytes": file_stat.st_size,
                        "created_at": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        "download_url": f"/api/v1/geometry/download/{filename}",
                    }
                )

    return {"files": files, "total_count": len(files)}
