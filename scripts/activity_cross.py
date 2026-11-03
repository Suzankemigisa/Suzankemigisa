import json
import os
import urllib.request

LOGIN = "Suzankemigisa"
OUT = "assets/activity-cross.svg"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
    }
  }
}
"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={
            "Authorization": f"bearer {os.environ['GH_TOKEN']}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as res:
        return json.load(res)["data"]["user"]["contributionsCollection"]


def render(c):
    counts = {
        "commits": c["totalCommitContributions"],
        "issues": c["totalIssueContributions"],
        "prs": c["totalPullRequestContributions"],
        "reviews": c["totalPullRequestReviewContributions"],
    }
    total = sum(counts.values()) or 1
    pct = {k: v / total for k, v in counts.items()}

    w, h, cx, cy, r = 520, 340, 260, 170, 110
    pts = {
        "reviews": (cx, cy - pct["reviews"] * r),
        "commits": (cx - pct["commits"] * r, cy),
        "issues": (cx + pct["issues"] * r, cy),
        "prs": (cx, cy + pct["prs"] * r),
    }
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in
                    (pts["reviews"], pts["issues"], pts["prs"], pts["commits"]))

    def label(x, y, anchor, key, name):
        return (
            f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="#B18FA2" '
            f'font-size="13">{round(pct[key] * 100)}%</text>'
            f'<text x="{x}" y="{y + 16}" text-anchor="{anchor}" fill="#FFFCFC" '
            f'font-size="13">{name}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="Segoe UI, Helvetica, Arial, sans-serif">
  <rect width="{w}" height="{h}" rx="10" fill="#040B14"/>
  <text x="20" y="30" fill="#FFFCFC" font-size="16" font-weight="600">Activity overview</text>
  <line x1="{cx - r}" y1="{cy}" x2="{cx + r}" y2="{cy}" stroke="#632148" stroke-width="1.5"/>
  <line x1="{cx}" y1="{cy - r}" x2="{cx}" y2="{cy + r}" stroke="#632148" stroke-width="1.5"/>
  <polygon points="{poly}" fill="#B18FA2" fill-opacity="0.35" stroke="#B18FA2" stroke-width="2"/>
  <text x="{cx}" y="{cy - r - 12}" text-anchor="middle" fill="#FFFCFC" font-size="13">Code review ({round(pct['reviews'] * 100)}%)</text>
  {label(cx - r - 14, cy - 6, "end", "commits", "Commits")}
  {label(cx + r + 14, cy - 6, "start", "issues", "Issues")}
  <text x="{cx}" y="{cy + r + 22}" text-anchor="middle" fill="#B18FA2" font-size="13">{round(pct['prs'] * 100)}%</text>
  <text x="{cx}" y="{cy + r + 38}" text-anchor="middle" fill="#FFFCFC" font-size="13">Pull requests</text>
</svg>"""


if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(fetch()))