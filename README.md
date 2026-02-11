# merger
This tool, "The Merger 1.0," is a high-precision Git release management suite designed to handle surgical code patching and version auditing. It eliminates the "noise" and "leaks" of standard Git merging by focusing on specific logical tasks.
This tool, "The Merger 1.0," is a high-precision Git release management suite designed to handle surgical code patching and version auditing. It eliminates the "noise" and "leaks" of standard Git merging by focusing on specific logical tasks.

Here is a breakdown of what the system does:

🚀 1. The Deployment Engine (Surgical Patching)
Tree-Based Injection: Instead of merging entire branches, it extracts the exact file changes (blobs) from selected commits and injects them into a new target version.

"In Base" Detection: Uses fingerprinting (Commit Message + Time) to identify if a task has already been deployed to your base branch, even if the Commit ID (SHA) has changed due to a previous cherry-pick.

Dependency Guard: Scans your selection against the branch history. If you pick a task that depends on an older, unselected commit, it issues a Conflict Warning to prevent broken code.

Smart Reminders: Analyzes the files being moved. If it sees .js files, dbm updates, or package.json changes, it automatically generates a post-deployment checklist (e.g., "Clear memcache," "Run npm install").

🔍 2. The Comparison Suite (Logic Gap Analysis)
Master-Validation: To identify what is "missing" in a version, it compares your source and target branches but filters the results against the Master branch. Only commits that exist on Master are considered relevant logic.

SHA Mapping: Because SHAs change across branches, the tool automatically maps "Sub-branch" commits back to their official Master SHA. This ensures you are always deploying the production-authorized version of the code.

One-Click Porting: Once a logic gap is identified, the "Port Missing Tasks" button automatically checks those official Master SHAs in the Deploy tab, sets the correct branches, and prepares the version for creation.

🛡️ 3. Technical & Security Standards
Zero-Knowledge Security: Your GitHub Token never leaves your browser. It is stored in localStorage and sent directly to GitHub’s API.

Deep Scan History: Fetches up to 300 commits per branch to ensure it finds the "Common Ancestor" even in very active repositories.

Jira Integration: Automatically detects ISCAR- ticket patterns in commit messages and generates direct links to your Atlassian boards.