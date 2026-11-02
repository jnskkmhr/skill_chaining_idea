# Risk-Conditioned Whole-Body Navigation

Research proposal for whole-body contact control using dense six-axis tactile feedback and a risk-conditioned contact planner on a humanoid robot.

[Open the slides](https://jnskkmhr.github.io/skill_chaining_idea/) · [Detailed research plan](Research_plan.md)

Use arrow keys or navigation buttons to move through 23 slides. Press **N** or click **Notes** for detailed explanations; the section links and slide selector support direct navigation. The risk slider illustrates lower-tail CVaR using explicitly stated synthetic outcomes. Print exports every slide to PDF.

Both the planner and controller run during deployment. Training starts with motion–terrain pairs, initializes planning from successful controller rollouts, and then uses navigation reinforcement learning with successful and failed episodes.

The self-contained `index.html` uses inline styles, scripts, and vector illustrations. Open it directly to preview. GitHub Pages serves the root of the `gh-pages` branch.

This is a research proposal. Diagrams and illustrative outcome distributions are not experimental results.

## Reproduce the risk figure

Run `uv run tools/generate_risk_figure.py` to regenerate the vector SVG/PDF from [the declared synthetic outcomes](figures/risk_example.json). The script uses its inline uv dependency specification. These outcomes illustrate the mathematics; they are not measurements from robot experiments. The HTML embeds the SVG and example data so the interactive slide works without a server.

Design guidance: [academic-pptx-skill](https://github.com/gabberflast/academic-pptx-skill/blob/main/SKILL.md) and [paper-figure](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/blob/main/skills/paper-figure/SKILL.md), adapted to HTML slides.
