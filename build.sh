# Build the Python files from the Protocol submodule
rm -rf src/pixelwalker_protocol
mkdir src/pixelwalker_protocol
protoc --proto_path=protocol/ --python_out=src/pixelwalker_protocol protocol/world.proto
