import argparse
import sys
from mazespace import Project, load_config
from mazespace.utils.persistence import save_session, load_session
from mazespace.config.loader import load_defaults

def main():
    parser = argparse.ArgumentParser(description="MazeSpace Arena - Configurable 3D Maze")
    parser.add_argument("--config", help="Path to config yaml/json file", default=None)
    parser.add_argument("--resume", action="store_true", help="Resume last session config")
    parser.add_argument("--reset", action="store_true", help="Reset to defaults")
    parser.add_argument("--headless", action="store_true", help="Run without UI")
    
    args = parser.parse_args()
    
    config = None
    
    # Load logic
    if args.reset:
        print("Resetting to defaults...")
        config = load_defaults()
        
    elif args.resume:
        print("Resuming last session...")
        config = load_session()
        if not config:
            print("No session found. Loading defaults.")
            config = load_defaults()
            
    elif args.config:
        print(f"Loading config from {args.config}...")
        try:
            config = load_config(args.config)
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
            
    else:
        # Default behavior: Try to resume, else defaults? 
        # Request said: "loads the last-used settings OR defaults if none exist"
        config = load_session()
        if not config:
            print("Loading defaults.")
            config = load_defaults()

    # Run App
    try:
        app = Project(config=config, headless=args.headless)
        app.run()
        
        # Save session on clean exit
        if not args.headless:
            save_session(app.config)
            
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(0)

if __name__ == "__main__":
    main()
