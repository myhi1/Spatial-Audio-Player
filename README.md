Spatial Audio Player
Developer: myhi1
Tech Stack: Python 3.12 (Tkinter & Pygame)
Project Overview
This application is an innovative music player that dynamically adjusts audio output based on the window's physical position on the screen. By moving the player, the user interacts with the sound in a 3D-like space, creating a tangible connection between the software interface and the audio experience.
Core Concept
The player treats the monitor as a sound stage. Moving the window left or right adjusts the speaker balance (panning), while moving it up or down controls the master volume. This "Spatial Audio" approach allows for physical interaction without needing traditional UI sliders.
Key Features
 * Horizontal Panning: Dragging the window to the left or right isolates the audio to the respective speaker.
   
 * Vertical Volume (Gain): Moving the window to the top increases volume, while moving it toward the bottom fades it out.
   
 * Muffled Minimize Effect: Automatically lowers the volume and applies a "muffled" effect when the app is minimized (simulating "Underground Mode").
   
 * Mouse Tracking Mode: An optional toggle that allows the audio parameters to change based on the mouse cursor position instead of the window location.
   
 * Dual-View Interface: Users can switch between a Full View (including playlist and album art) and a Compact Mode (a small remote-style window).
   
 * Playlist Management: Built-in manager supporting bulk file imports and automatic track progression.
   
Development Journey (Changelog)
Phase 1: Foundations
The initial logic focused on basic Panning Formulas. If the window is at the far left, the left channel is at 100% and the right is at 0%. This phase also introduced the logic for detecting when the window is minimized to trigger the muffled effect.
Phase 2: Audio Physics
To make the experience more professional, I replaced simple linear calculations with Exponential Scaling. This makes volume and panning transitions feel more natural to the human ear. I also added Smoothing Algorithms to prevent audio "pops" during rapid window movement.
Phase 3: Visual Identity
The UI was designed with a Cyberpunk Dark Mode aesthetic. I integrated standard media controls and ensured the interface remained responsive while the audio engine calculated spatial coordinates in the background.
Phase 4: Optimization
In the final phase, I added a settings menu to allow users to toggle specific effects. I also prioritized a Compact Mode to ensure the player doesn't obstruct the user's workspace while they are dragging it around.

Technical Challenges & Solutions

 * Audio Engine Trade-off: I discovered that pygame.mixer.music supports seeking (time-skipping) but not panning, while pygame.mixer.Sound supports panning but not seeking. I prioritized the Spatial Experience and chose the Sound engine. While seeking was removed, the 3D separation became much more precise.
   
 * Permissions & Stability: I initially used the keyboard library for global hotkeys, but it required Admin privileges and caused crashes. I replaced this with standard root.bind events, making the app safer and more stable for all users.
   
 * Window Behavior: Frameless windows were difficult to move on some versions of Windows. I opted for a modern, standard window frame that is optimized for frequent repositioning.
   
The St:
The idea for this project came to me as a sudden spark—a way to make digital sound feel like a physical object. To capture the idea before it faded, I sketched the logic on paper the very next day. During development, I realized that by using the Sound object engine, I could manipulate the Left and Right channels entirely independently. This opens up future possibilities for playing two different audio streams simultaneously from different speakers based on window proximity.

Installation & Usage
 * Ensure Python 3.x is installed. 
 * Install the Pygame library: pip install pygame
 * Run the script: python music.py
