# Security Boundary

Only `strategy.*` messages cross this boundary. Execution commands, direct agent targets, file operations, GitHub operations, and unrecognized message types return `ERR-STR-008`. ADR text is screened before any write; safety failure returns `ERR-STR-004` and does not create a file.
