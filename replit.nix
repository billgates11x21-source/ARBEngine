{ pkgs }: {
  deps = [
    pkgs.python310
    pkgs.python310Packages.pip
    pkgs.python310Packages.uvicorn
    pkgs.python310Packages.fastapi
    pkgs.python310Packages.numpy
    pkgs.python310Packages.pandas
    pkgs.python310Packages.requests
    pkgs.python310Packages.websocket-client
    pkgs.python310Packages.python-dotenv
    pkgs.python310Packages.aiohttp
    pkgs.nodejs-16_x
    pkgs.nodePackages.npm
    pkgs.bash
    pkgs.curl
    pkgs.lsof
  ];
}