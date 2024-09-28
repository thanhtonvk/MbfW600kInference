
import onnxruntime
import os
def onnx_model_inference(model: str):
    model_path = os.path.abspath(model)
    session_options = onnxruntime.SessionOptions()
    session_options.graph_optimization_level = onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL
    execution_providers =['CUDAExecutionProvider', 'CPUExecutionProvider']
    # execution_providers =['CPUExecutionProvider']
    session = onnxruntime.InferenceSession(
        model_path, session_options, providers=execution_providers
    )
    print(session.get_providers())
    return session