# flake.nix
{
  description = "Python";

  inputs = {
    # Nixpkgs provides the available packages
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05"; # You can specify the version you want
  };

  outputs = { self, nixpkgs, ... }:
    let
      # Import the nixpkgs package set
      pkgs = import nixpkgs {
        system = "x86_64-linux"; # Or "aarch64-linux" depending on your architecture
      };
    in
    {
      # Define the development shell
      devShell.x86_64-linux = pkgs.mkShell {
        buildInputs = [
          pkgs.python3 # Use Python 3
          pkgs.python3Packages.pip # Install pip
        ];
      };
    };
}
