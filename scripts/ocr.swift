// macOS Vision OCR. usage: scripts/ocr <image.png>  ->  one line per text box: "x y w h<TAB>text"
// (pixel coords of the box, origin top-left). Build once: swiftc -O scripts/ocr.swift -o scripts/ocr
import Foundation
import Vision
import AppKit

let url = URL(fileURLWithPath: CommandLine.arguments[1])
guard let img = NSImage(contentsOf: url), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { exit(1) }
let W = Double(cg.width), H = Double(cg.height)
let req = VNRecognizeTextRequest()
req.recognitionLevel = .accurate
req.recognitionLanguages = ["en-US"]
req.usesLanguageCorrection = false
try VNImageRequestHandler(cgImage: cg).perform([req])
for o in req.results ?? [] {
    guard let t = o.topCandidates(1).first?.string else { continue }
    let b = o.boundingBox
    print("\(Int(b.minX * W)) \(Int((1 - b.maxY) * H)) \(Int(b.width * W)) \(Int(b.height * H))\t\(t)")
}
