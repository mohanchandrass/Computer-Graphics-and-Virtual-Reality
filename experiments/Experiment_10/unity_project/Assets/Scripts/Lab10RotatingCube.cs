using UnityEngine;

/// <summary>
/// Experiment 10 – 3D Viewing Pipeline (Orthographic vs Perspective)
/// Attach to the rotating cube.  The cube spins continuously so both
/// projection cameras can demonstrate the viewing pipeline in real time.
/// </summary>
public class Lab10RotatingCube : MonoBehaviour
{
    [Tooltip("Rotation speed in degrees per second around each axis.")]
    public Vector3 rotationSpeed = new Vector3(20f, 35f, 10f);

    void Update()
    {
        transform.Rotate(rotationSpeed * Time.deltaTime, Space.World);
    }
}

