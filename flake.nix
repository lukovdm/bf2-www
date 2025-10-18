{
  description = "BF2 djangocms website";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      devShell = pkgs.mkShell {
        nativeBuildInputs = [ pkgs.bashInteractive ];
        buildInputs = with pkgs; [
          python311
          gtranslator
          poedit
          poetry
          flyctl
          openssl
          httpie
          stdenv.cc.cc.lib
          gcc
        ];
        # Make GCC's C++ runtime visible to dynamically loaded wheels (e.g., libsass)
        shellHook = ''
          export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc.lib ]}:$LD_LIBRARY_PATH
        '';
      };
    });
}