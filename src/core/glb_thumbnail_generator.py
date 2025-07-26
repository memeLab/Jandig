from io import BytesIO

import numpy as np
import pyrender
import trimesh
from PIL import Image

from core.models import Object


def create_camera(scene: pyrender.Scene):
    """Create a camera for the given pyrender scene."""
    # Calculate the scene bounds to position camera appropriately
    scene_bounds = scene.bounds
    scene_center = (scene_bounds[0] + scene_bounds[1]) / 2.0
    scene_scale = np.linalg.norm(scene_bounds[1] - scene_bounds[0])

    # Position camera to view the entire model from a front-angled view
    # Place camera slightly elevated and in front of the model
    camera_distance = (
        scene_scale * 0.9
    )  # Very close for maximum detail and tight framing

    # Position camera in front and slightly above the model
    # Assuming Y is up, Z is forward/back, X is left/right
    camera_position = scene_center + np.array(
        [
            camera_distance * 0.3,  # Slightly to the right
            camera_distance * 0.4,  # Elevated above
            camera_distance * 1.0,  # In front of the model
        ]
    )

    # Create camera with wider field of view for better framing
    camera = pyrender.PerspectiveCamera(yfov=np.pi / 4.0, aspectRatio=1.0)  # 45 degrees

    # Create look-at matrix pointing at the scene center
    # Use a proper look-at transformation
    eye = camera_position
    target = scene_center
    up_vector = np.array([0, 1, 0])  # Y is up

    # Calculate camera orientation
    forward = target - eye
    forward = forward / np.linalg.norm(forward)

    right = np.cross(forward, up_vector)
    right = right / np.linalg.norm(right)

    up = np.cross(right, forward)
    up = up / np.linalg.norm(up)

    # Create camera pose matrix
    camera_pose = np.eye(4)
    camera_pose[:3, 0] = right
    camera_pose[:3, 1] = up
    camera_pose[:3, 2] = -forward  # OpenGL uses negative Z for forward
    camera_pose[:3, 3] = eye

    return camera, camera_pose, camera_position, camera_distance


def create_lighting(scene: pyrender.Scene, camera_position, camera_distance):
    scene_bounds = scene.bounds
    scene_center = (scene_bounds[0] + scene_bounds[1]) / 2.0
    # Key light (main directional light from camera direction)
    key_light = pyrender.DirectionalLight(color=np.ones(3), intensity=2.5)
    key_light_pose = np.eye(4)
    key_light_pose[:3, 3] = camera_position
    scene.add(key_light, pose=key_light_pose)

    # Fill light (from the opposite side for softer shadows)
    fill_light = pyrender.DirectionalLight(color=np.ones(3), intensity=1.2)
    fill_light_pose = np.eye(4)
    fill_light_pose[:3, 3] = scene_center + np.array(
        [-camera_distance * 0.5, camera_distance * 0.2, -camera_distance * 0.5]
    )
    scene.add(fill_light, pose=fill_light_pose)

    # Top light for better definition
    top_light = pyrender.DirectionalLight(color=np.ones(3), intensity=0.8)
    top_light_pose = np.eye(4)
    top_light_pose[:3, 3] = scene_center + np.array([0, camera_distance, 0])
    scene.add(top_light, pose=top_light_pose)

    # Ambient light for overall illumination
    ambient_light = pyrender.DirectionalLight(color=np.ones(3), intensity=0.3)
    scene.add(ambient_light)


def generate_thumbnail(obj: Object):
    # Read the file as GLB
    obj_bytes = BytesIO()
    obj.source.open()
    obj_bytes.write(obj.source.read())
    obj.source.close()
    obj_bytes.seek(0)  # Reset the BytesIO stream position
    # Create file from bytes
    return generate_thumbnail_from_bytes(obj_bytes)


def generate_thumbnail_from_bytes(obj_bytes) -> Image:
    """Generate a thumbnail image from a GLB file."""
    size = (400, 400)

    # Load the GLB file using trimesh
    scene = trimesh.load_mesh(obj_bytes, file_type="glb")
    mesh = pyrender.Mesh.from_trimesh(scene)

    # Create pyrender scene
    pyrender_scene = pyrender.Scene()
    pyrender_scene.add(mesh)

    # Create camera and lighting
    camera, camera_pose, camera_position, camera_distance = create_camera(
        pyrender_scene
    )
    pyrender_scene.add(camera, pose=camera_pose)

    create_lighting(pyrender_scene, camera_position, camera_distance)

    # Set up renderer
    renderer = pyrender.OffscreenRenderer(*size)
    color, depth = renderer.render(pyrender_scene)

    # Convert to PIL Image and save
    image = Image.fromarray(color, "RGB")

    # Clean up
    renderer.delete()

    return image
