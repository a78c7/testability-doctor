// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "SwiftUnsupportedExample",
    products: [
        .library(name: "SwiftUnsupportedExample", targets: ["SwiftUnsupportedExample"])
    ],
    targets: [
        .target(name: "SwiftUnsupportedExample")
    ]
)
