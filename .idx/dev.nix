# To learn more about how to use Nix to configure your environment
# see: https://firebase.google.com/docs/studio/customize-workspace
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    # pkgs.go
    # pkgs.python311
    # pkgs.python311Packages.pip
    # pkgs.nodejs_20
    # pkgs.nodePackages.nodemon
    # pkgs.python311Packages.streamlit
    # pkgs.python311Packages.watchdog
    # pkgs.python311Packages.python-dotenv
    # pkgs.python311Packages.psycopg2-binary
    # pkgs.python311Packages.python-jose
    # pkgs.python311Packages.passlib
    # pkgs.python311Packages.bcrypt
    # pkgs.python311Packages.cryptography
    # pkgs.python311Packages.google-auth
    # pkgs.python311Packages.google-auth-oauthlib
    # pkgs.python311Packages.google-api-python-client
    # pkgs.python311Packages.google-cloud-storage
    # pkgs.python311Packages.vertexai
    # pkgs.python311Packages.openai
    # pkgs.python311Packages.anthropic
    # pkgs.python311Packages.google-generativeai
    # pkgs.python311Packages.pillow
    # pkgs.python311Packages.pyaudio
    # pkgs.python311Packages.requests
    # pkgs.python311Packages.speechrecognition
    # pkgs.python311Packages.streamlit-extras
    # pkgs.python311Packages.streamlit-webrtc
    # pkgs.python311Packages.elevenlabs
    # pkgs.python311Packages.soundfile
    # pkgs.python311Packages.av
    # pkgs.python311Packages.flask
  ];

  # Sets environment variables in the workspace
  env = {};
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      # "vscodevim.vim"
    ];

    # Enable previews
    previews = {
      enable = true;
      previews = {
        # web = {
        #   # Example: run "npm run dev" with PORT set to IDX's defined port for previews,
        #   # and show it in IDX's web preview panel
        #   command = ["npm" "run" "dev"];
        #   manager = "web";
        #   env = {
        #     # Environment variables to set for your server
        #     PORT = "$PORT";
        #   };
        # };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        # Example: install JS dependencies from NPM
        # npm-install = "npm install";
      };
      # Runs when the workspace is (re)started
      onStart = {
        # Example: start a background task to watch and re-build backend code
        # watch-backend = "npm run watch-backend";
      };
    };
  };
}
