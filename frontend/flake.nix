# flake.nix
{
  description = "Svelte + TypeScript development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05"; # You can choose a specific Nixpkgs revision or channel
  };

  outputs = { self, nixpkgs, ... }:
    let
      pkgs = import nixpkgs {
        system = "x86_64-linux"; # Use "aarch64-linux" for ARM-based systems, or another system if needed
      };
    in
    {
      devShell.x86_64-linux = pkgs.mkShell {
        buildInputs = [
          pkgs.nodejs # Node.js runtime for Vite
          pkgs.yarn # Yarn package manager (optional, can use npm as well)
        ];
      };
    };
}
