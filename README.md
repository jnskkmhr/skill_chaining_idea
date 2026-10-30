# Risk-Conditioned Whole-Body Navigation

Research proposal for whole-body contact control using dense six-axis tactile feedback and a risk-conditioned contact planner on a humanoid robot.

[Open the slides](https://jnskkmhr.github.io/skill_chaining_idea/) · [Detailed research plan](Research_plan.md)

Use arrow keys or navigation buttons to move through 22 slides. The risk slider illustrates lower-tail CVaR using explicitly stated synthetic outcomes. Print exports every slide to PDF.

Both the planner and controller run during deployment. Training starts with motion–terrain pairs, initializes planning from successful controller rollouts, and then uses navigation reinforcement learning with successful and failed episodes.

The self-contained `index.html` uses inline styles, scripts, and vector illustrations. Open it directly to preview. GitHub Pages serves the root of the `gh-pages` branch.

This is a research proposal. Diagrams and illustrative outcome distributions are not experimental results.
