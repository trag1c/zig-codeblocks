Hi, I'm trying to rewrite a Python project of mine in Zig.

Here's the original project: 
```py
print("Hello, World!")
```
And here's my attempt at the Zig rewrite:
```zig
const std = @import("std");
pub fn main() !void {
    std.debug.print("Hello, World!\n", .{});
}
```
I'm still learning Zig, so I'm not sure if this is the best way to do it.