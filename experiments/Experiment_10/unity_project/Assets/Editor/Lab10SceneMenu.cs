using UnityEditor;
using UnityEngine;

public static class Lab10SceneMenu
{
    [MenuItem("CGVR Labs/Lab 10 - Run 3D Viewing Pipeline")]
    private static void RunLab10()
    {
        if (EditorApplication.isPlaying) return;
        EditorApplication.isPlaying = true;
    }

    [MenuItem("CGVR Labs/Lab 10 - Validate Setup")]
    private static void Validate()
    {
        bool hasShader = Shader.Find("CGVR/Lab10/FaceColors") != null;
        if (hasShader)
            Debug.Log("[Lab 10] Validation Success: CGVR/Lab10/FaceColors shader is active and ready.");
        else
            Debug.LogWarning("[Lab 10] CGVR/Lab10/FaceColors shader not loaded yet. Unity will compile it shortly.");
    }
}
