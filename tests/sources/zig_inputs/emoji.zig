const std = @import("std");

pub fn main() !void {
    const stdout = std.io.getStdOut().writer();

    const greeting = "Hello, 🌍!\n";
    try stdout.print("{s}", .{greeting});

    const emoji_identifier = "✅ This is a test string with emojis 🚀🔥\n";
    try stdout.print("{s}", .{emoji_identifier});
}
