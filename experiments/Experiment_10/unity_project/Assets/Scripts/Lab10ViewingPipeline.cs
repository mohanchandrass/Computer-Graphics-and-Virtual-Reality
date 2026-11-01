using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Experiment 10 – 3D Viewing Pipeline
/// Creates two cameras side-by-side at runtime:
///   Left  half → Orthographic  projection
///   Right half → Perspective   projection  (FOV 45°)
/// Both look at the same rotating coloured cube, demonstrating the full
/// 3D Viewing Pipeline:  Object → World → Camera → Clip → NDC → Viewport.
/// </summary>
public class Lab10ViewingPipeline : MonoBehaviour
{
    [Header("Cube (auto-found by tag 'Lab10Cube')")]
    public Transform cubePivot;

    [Header("Camera settings")]
    public float orthographicSize = 2.5f;
    public float perspectiveFOV  = 45f;
    public float cameraDistance  = 7f;
    public float cameraHeight    = 3f;

    // Private runtime cameras
    private Camera _orthoCam;
    private Camera _perspCam;

    void Awake()
    {
        // ── Find the cube if not set in Inspector ──────────────────────────
        if (cubePivot == null)
        {
            var tagged = GameObject.FindWithTag("Lab10Cube");
            if (tagged) cubePivot = tagged.transform;
        }

        // ── Build cameras ──────────────────────────────────────────────────
        _orthoCam = BuildCamera("OrthoCamera",  new Rect(0f, 0f, 0.5f, 1f), isOrtho: true,  depth: 0);
        _perspCam = BuildCamera("PerspCamera",  new Rect(0.5f, 0f, 0.5f, 1f), isOrtho: false, depth: 1);

        // Disable the camera this script is on (it's just a host)
        var hostCam = GetComponent<Camera>();
        if (hostCam) hostCam.enabled = false;
    }

    Camera BuildCamera(string goName, Rect viewportRect, bool isOrtho, int depth)
    {
        GameObject go = new GameObject(goName);
        go.transform.SetParent(transform.parent);

        Vector3 lookTarget = cubePivot ? cubePivot.position : Vector3.zero;
        go.transform.position = new Vector3(4f, cameraHeight, cameraDistance);
        go.transform.LookAt(lookTarget);

        Camera cam = go.AddComponent<Camera>();
        cam.rect = viewportRect;
        cam.depth = depth;
        cam.nearClipPlane = 0.1f;
        cam.farClipPlane  = 100f;
        cam.clearFlags = (depth == 0)
            ? CameraClearFlags.SolidColor
            : CameraClearFlags.Depth;
        cam.backgroundColor = new Color(0.08f, 0.08f, 0.12f);

        if (isOrtho)
        {
            cam.orthographic = true;
            cam.orthographicSize = orthographicSize;
        }
        else
        {
            cam.orthographic = false;
            cam.fieldOfView  = perspectiveFOV;
        }

        return cam;
    }
}

