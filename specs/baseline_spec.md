You are a senior robotics + LLM engineer. Build a complete, runnable Python project that demonstrates a local PyBullet robot-arm simulation where a Franka Panda robot can pick up a cube from a table.



Requirements:

\- Use PyBullet GUI mode.

\- Scene must include plane, table, Panda robot, and one default cube object.

\- Provide a text-based CLI loop.

\- Integrate Foundry Local using the OpenAI-compatible chat completions endpoint.

\- The LLM must output strict JSON actions only, never Python.

\- Supported actions:

&#x20; - describe\_scene()

&#x20; - move\_ee(target\_xyz, target\_rpy, speed)

&#x20; - open\_gripper(width)

&#x20; - close\_gripper(force)

&#x20; - pick(object)

&#x20; - place(target\_xyz)

&#x20; - reset()

\- Validate all actions before execution.

\- Use inverse kinematics and smooth joint interpolation.

\- Include safety clamps.

\- Package with:

&#x20; - src/ structure

&#x20; - requirements.txt

&#x20; - README.md

\- Default entry point:

&#x20; - python -m src.app

\- Acceptance criterion:

&#x20; - user types “pick up the cube”

&#x20; - robot successfully picks and lifts the cube at least once.



Deliver:

1\. architecture summary

2\. file tree

3\. full code for each file

4\. README with Foundry Local setup and run commands

