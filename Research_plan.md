# Risk-conditioned whole-body navigation with tactile feedback

Updated October 30, 2026. Research proposal; no performance claims are established.

## 1. Research objective

Train a humanoid to navigate from a start state to a goal using feet, hands, and other intended body contacts. The robot should respond to measured support conditions and change its contact strategy when the user changes its risk preference.

The deployed system is hierarchical. A learned contact planner chooses upcoming body–terrain contacts. A learned whole-body controller executes those commands using terrain observations, robot state, and tactile feedback. Both policies remain active during deployment and receive new observations repeatedly.

The two research hypotheses are:

1. **Tactile contact control:** spatial and temporal six-axis tactile observations improve contact execution and recovery beyond proprioception, terrain perception, normal-pressure maps, and a single total six-axis force/torque measurement.
2. **Risk-conditioned contact planning:** a planner trained with a risk-dependent objective changes its contact strategy on the same navigation problem. Conservative settings should reduce poor outcomes when safer alternatives are available, potentially at a cost in time or energy.

The combined hypothesis is that measured support conditions improve subsequent risk-conditioned decisions, not only immediate stabilization. Each component must first demonstrate value separately.

## 2. Relationship to prior work

[ACP](https://arxiv.org/html/2610.31608v1) supplies the architectural starting point. Its planner uses supervised learning on hindsight contact labels from successful controller executions. Its controller uses RL. Motion sources and AME-policy data contribute to its initial reference collection; they are distinct from the controller-rollout supervision used by its planner.

[TactileStep](https://arxiv.org/abs/2609.28959) and [Tac4Loco](https://arxiv.org/abs/2608.15766) establish strong prior work on sole sensing for humanoid locomotion. The available sensor reports three force and three torque components at every sensing element. Our question is whether this spatial six-axis information improves recovery beyond pressure sensing or a total foot force/torque measurement; the richer sensor alone does not establish a control contribution. The primary experiment tests contact recovery. A separate extension tests whether tactile feedback also improves future contact decisions.

[Risk-aware quadrupedal locomotion](https://arxiv.org/abs/2309.14246) already demonstrates adjustable risk through distributional RL. Our proposed extension is risk-conditioned whole-body contact selection on a humanoid under uncertain support, with tactile observations informing execution and planning. CVaR itself is not a novel algorithmic contribution.

## 3. Task and scope

The command is a target robot-base position and heading, plus a risk setting. The position includes horizontal location and height. Use the same command for all locomotion behaviors; do not introduce a separate jump or climb command.

The initial benchmark has locally observable route alternatives: a ledge and ramp, a gap and detour, sparse footholds, or a low passage followed by a climb. Local contact planning is not a complete solution to arbitrary long-range maze navigation. Keep that problem outside the initial claim.

The actor observes terrain geometry, recent robot state, previous actions, and available tactile signals. Physical properties such as friction and compliance may be hidden. Their true simulator values can support training diagnostics or a privileged critic, but must not silently enter the deployed actor.

A battery measurement, if added later, represents physical state. Risk preference represents the operator's tolerance for poor outcomes. Low battery does not imply a unique risk setting: an energy-saving shortcut and a conservative detour can conflict. The first study holds robot limits fixed and varies the risk command explicitly.

## 4. Deployed interfaces

| Component | Inputs | Outputs |
| --- | --- | --- |
| Contact planner | Local terrain points; base and joint state history; prior actions; tactile history; goal pose; risk setting | Next contact position and active flag for each contact-enabled body |
| Whole-body controller | Contact command; local terrain; robot state and action history; tactile history | 29 joint position targets for the G1 model |
| Joint controller | Joint targets and measured joint state | Actuator torques from proportional–derivative control, within robot limits |

Start with nine contact-enabled bodies: two feet, two hands, two knees, two elbows, and the pelvis. Use only contact geometries present and validated in the actual G1 asset. Ball-hand geometry is a mechanical contact choice, not a tactile sensor.

Each body receives one XYZ contact target and a binary active flag for a look-ahead horizon initially set to 1.5 seconds. An inactive target is masked. This interface does not prescribe a full limb trajectory or an exact touchdown time. If experiments show that contact order or timing is ambiguous, evaluate an explicit timing extension; do not introduce it without evidence.

Target coordinates use an origin at the robot base, vertical aligned with gravity, and horizontal axes rotated by the base heading. Do not rotate vertical with base roll or pitch. A terrain point selected in one frame must be transformed consistently when the base moves. Maintain target identity across updates when a contact is being executed, or explicitly record a target revision; otherwise contact-error measurements can be misleading.

Use an attention-based terrain encoder as the initial architecture. Each body query predicts a categorical distribution over observed terrain points and a separate active probability. Sample these during planner RL so the executed action has a defined probability. Controller training must expose it to the same command distribution. During evaluation, document whether commands are sampled or chosen deterministically.

Start with a 50 Hz interface for both policies and measure inference cost, target changes, and action smoothness. Adjust the planner rate or command persistence only if needed. Terrain observations must contain intended contact surfaces. A single ground height map is insufficient for some overhangs and vertical hand supports; begin with visible top surfaces, then validate a representation that includes additional surfaces before expanding the task set.

## 5. Dense six-axis tactile observations

The available tactile hardware reports **six components at each sensing element: three forces and three torques**. Treat this as a spatial array of local force/torque measurements, not a normal-pressure map or a single force/torque sensor at the ankle. A force vector and a torque vector together form a **wrench**.

For each element, define its calibrated location, axes, and the reference point about which torque is reported. Store the force components in newtons and torque components in newton-metres. State whether the sign denotes the environment acting on the robot or the opposite; use the same convention in simulation and hardware. Preserve the spatial arrangement and a short signal history. The observation is a time sequence of element locations and six-component measurements, with masks for unavailable or invalid elements.

Three-axis forces provide tangential force as well as normal loading when resolved against a known surface normal. Torques provide moments about the element reference point. These are directly measured channels. Slip velocity, the available friction limit, terrain material, and sinking depth are not direct outputs of this sensor. Estimate useful contact conditions from tactile history and robot motion, and validate those estimates against independent measurements. Tangential force divided by normal force is a loading ratio, not the friction coefficient or a known margin to slip.

The controller should learn how local loading patterns relate to sliding, foot rotation, partial support, and recovery. Candidate corrections include redistributing load, adjusting ankle action, and repositioning the foot. A local torque can arise from force acting away from its reference point; do not automatically interpret every torque channel as pure contact twisting. Test whether local torque information adds value beyond dense three-axis force measurements.

When constructing a total foot wrench, rotate element measurements into one frame and shift moments to one chosen origin before summing. Include the moment produced by each force's offset from that origin. Check the sensor's torque definition to avoid counting this contribution twice. See [Modern Robotics: Wrenches](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-4-wrenches/) for frame and reference-point conventions. If a pressure or center-of-pressure baseline is used, derive it with an explicit contact-surface model and mask unloaded contacts.

Calibrate spatial resolution, six-axis gains and offsets, force–torque cross-axis coupling, saturation, filtering, sampling rate, latency, and failed elements. The simulator must reproduce the signals available at each physical element. A total rigid-body contact wrench alone is not a dense tactile array. Contact forces and their application points may support element-level force and moment calculations, but the sensor's internal deformation and measurement response must be calibrated. Do not invent independent per-element torque channels from an aggregate contact signal.

Introduce conditions progressively: rigid terrain with varied friction and partial footholds; disturbances that cause sliding or foot rotation; calibrated compliant supports; then deformable or granular terrain with validated yielding behavior. Add measured translation and rotation of the foot relative to its support surface to the recovery evaluation.

The sensor specification confirms channel content, not placement on every robot body. Start with the planned foot instrumentation. Direct hand-tactile recovery claims require instrumented hands. Keep the initial planner output as contact positions and active flags: measured wrenches enrich feedback without requiring planned force or torque targets.

## 6. Stage1: train the contact-conditioned controller

Use the existing motion library and mimic infrastructure as training resources. Each example must pair a retargeted G1 motion with the terrain on which it is intended to execute. Preserve the existing dataset fields and conventions, including `terrain_position`, `terrain_dimension`, and `terrain_quat`, or the existing terrain-mesh representation. Validate joint ordering, quaternion conventions, timing, robot geometry, floor height, and motion–terrain alignment through the existing loaders.

Kinematic proximity can propose contact labels, but dynamic execution must verify them. Define contact onset using measured contact and a minimum duration. For inclined or vertical surfaces, use an appropriate contact normal or force magnitude; a vertical-force-only rule may miss hand support. Record the body, surface, location, and duration of each intended contact.

Train the controller with RL using reference contact commands. Reference joint and base motion can supply shaping rewards and reset states during initialization. The deployed actor receives the contact command and sensor observations, not reference joint trajectories. Avoid hidden reference phase inputs that disappear at deployment.

Objectives cover active-contact position accuracy, actual intended support, body stability, progress, actuator effort, and impact. Position tracking alone cannot establish that a foot or hand is bearing load. Exclude allowed support contacts from generic collision penalties while penalizing unintended collisions.

Expose the controller to altered contact targets and disturbances near demonstrated states. Randomize friction, foothold edges, pushes, and sensor errors. Validate recovery before increasing terrain complexity. Reduce dependence on full-motion rewards as contact-conditioned behavior becomes reliable, and test the controller without trajectory inputs before planner integration.

## 7. Stage2: initialize the contact planner

Execute the trained controller on paired terrains and record observations, commands, actual body contacts, and episode outcomes. Begin with reference contact commands.

For successful episodes, look forward from each recorded timestep to the next sustained contact for each body within the chosen horizon. Express that contact in the frame at the recorded timestep. Retain targets that are observable in the planner's terrain representation; use an active flag to indicate whether a valid upcoming contact exists.

Fit the planner with contact-point classification and active-flag classification losses. Gradually replace reference commands with predicted commands while the controller adapts. Relabel actual successful executions as behavior improves. Split training and validation by terrain and source motion, not randomly adjacent frames of the same clip.

These labels demonstrate contacts the controller can achieve. They do not establish the failure probability of those contacts. Keep successful-contact supervision and risk estimation as separate data uses.

## 8. Stage3: train risk-conditioned contact planning

Train on procedural goal-reaching environments, including environments without a paired motion trajectory. Sample start, goal, terrain geometry, hidden physical variation, and risk setting. The planner proposes contact commands; the controller executes them.

Initially freeze the controller. This isolates the planner's learning problem and makes return distributions easier to compare. Then alternate planner training and controller adaptation if needed. After changing the controller, collect fresh rollouts: contact feasibility and failure probabilities have changed.

Train the planner from all on-policy episodes, including failures. Successful episodes can still supply an auxiliary contact-supervision loss, but they must not be the only observations used for risk learning. Record the active risk setting, planner action probabilities, contact commands, episode return, and termination cause.

Navigation return rewards progress and goal completion and penalizes time, falls, unintended collisions, and excessive effort. Keep reward terms fixed across the risk sweep. Include a timeout and report standing still or avoiding the task as failures; conservatism must not be rewarded through inaction.

Use a curriculum that offers multiple feasible strategies. If every scene has only one viable route, changing risk cannot produce meaningful route selection. Vary support reliability repeatedly for matched geometry so the training distribution contains uncertainty relevant to the decision.

## 9. Mathematical formulation of the contact planner

### 9.1 Physical state, planner action, and partial observations

Let **t** index planner updates. Let **xₜ** be the full physical state: robot configuration and velocity, terrain and contact state, friction and compliance parameters, controller memory, and the remaining episode time. Including hidden physical parameters and controller memory is necessary for a Markov model; a terrain scan and joint state alone need not be Markov.

Let **aₜ** be the planner action: a terrain contact position and an active flag for each of the nine contact-enabled bodies. Let **g** be the fixed goal pose. Let **α ∈ (0, 1]** be the risk setting, held fixed within an episode. Let **θ** denote planner parameters and **φ** the parameters of the fixed whole-body controller. The controller executes contact commands through joint actions; it is part of the planner's environment.

Let **Pφ** be the physical transition model induced by that controller and the simulator. At a fixed planner update interval:

\[
x_{t+1}\sim P_\phi(\cdot\mid x_t,a_t).
\]

The task state can be written as **sₜ = (xₜ, g, α)**. Goal and risk are constant context during an episode. Risk changes the planner's action distribution and learning objective; it does not change the physical transition for a fixed state and contact action. Goal-dependent termination stops the episode on success; failures and timeout also terminate it.

The deployed planner does not observe all of xₜ. Let **oₜ** contain the terrain map, robot proprioception, and dense six-axis tactile signals. Let **hₜ = (o₀, a₀, …, aₜ₋₁, oₜ)** be the observation/action history. The planner is:

\[
a_t\sim\pi_\theta(\cdot\mid h_t,g,\alpha).
\]

The full-state simulator admits an MDP formulation; deployment is a **partially observable MDP (POMDP)** because friction, compliance, and unobserved terrain state are hidden. A finite history or recurrent encoder is an approximation to the information in hₜ, not proof that its features form a sufficient Markov state. If the controller changes during training, Pφ changes; freeze it initially and collect fresh planner data after controller updates.

### 9.2 Discounted episode return and the risk-neutral objective

Let **rₜ = r_g(xₜ, aₜ, xₜ₊₁)** be the task reward, **γ ∈ (0, 1]** the discount factor, and **T** the number of planner steps until termination. Define the random discounted episode return under θ and α as **Gθ,α**:

\[
G_{\theta,\alpha}=\sum_{t=0}^{T-1}\gamma^t r_t.
\]

Reward goal progress and completion; penalize time, falls, unintended collisions, and excessive effort. Specify how controller-step rewards are accumulated into each planner-step reward if the two policies run at different rates. Keep the reward weights, time discretization, and discount factor fixed when comparing risk settings.

Standard risk-neutral RL optimizes:

\[
\max_\theta\;\mathbb{E}[G_{\theta,\alpha}].
\]

The expectation averages over the declared start/terrain distribution, physical randomization, disturbances, and stochastic actions. **The return is the discounted sum. Expected return and CVaR are different ways of evaluating the distribution of that same sum.** CVaR is not an additional physical reward at every timestep. γ weights future rewards; it is not the risk-preference parameter.

### 9.3 Lower-tail CVaR of return

Use **α** as the fraction of lowest-return outcomes to average. Smaller α emphasizes poor episodes; α = 1 includes all episodes. Let **η** be a scalar return threshold, and define the positive part **(z)⁺ = max(z, 0)** for any scalar z. Lower-tail CVaR is:

\[
\operatorname{CVaR}^{\downarrow}_{\alpha}(G_{\theta,\alpha})
=\max_{\eta\in\mathbb{R}}\left\{
\eta-\frac{1}{\alpha}\mathbb{E}\left[(\eta-G_{\theta,\alpha})^+\right]
\right\}.
\]

This definition also handles discrete returns and ties by taking the required fraction of probability mass at the tail boundary. Writing only a conditional expectation below a quantile can mishandle such ties. At α = 1 the expression equals the expected return. At α = 0.1 it averages the worst 10% of return probability mass. Larger lower-tail CVaR is preferred.

The main formulation is a risk-sensitive return objective:

\[
\max_\theta\;\operatorname{CVaR}^{\downarrow}_{\alpha}(G_{\theta,\alpha}).
\]

It replaces the mean-return criterion; it does not add a separate CVaR reward. Low return can reflect delay, energy use, or failure, depending on reward design. Consequently, return CVaR is not itself a bound on fall probability. This lower-tail family covers risk aversion through risk neutrality, not explicit risk seeking. See [Chow et al., Risk-Sensitive and Robust Decision-Making](https://papers.neurips.cc/paper_files/paper/2015/file/64223ccf70bbb65a3a4aceac37e21016-Paper.pdf).

### 9.4 Optional mean–CVaR objective and training across risk settings

A combined objective is also valid. Define **λ ∈ [0, 1]** as a fixed weight between the mean and the lower-tail criterion:

\[
\max_\theta\;(1-\lambda)\mathbb{E}[G_{\theta,\alpha}]
+\lambda\operatorname{CVaR}^{\downarrow}_{\alpha}(G_{\theta,\alpha}).
\]

λ = 0 gives mean-return training; λ = 1 gives the chosen CVaR-only method. A fixed intermediate λ provides an ablation for the mean/tail tradeoff. Both terms favor larger returns, so the CVaR term has a plus sign. Equivalently, subtracting the shortfall between mean and CVaR from the mean produces this convex combination. Keep λ fixed in the initial study and use α as the single user command. See [Chow and Ghavamzadeh, Algorithms for CVaR Optimization in MDPs](https://proceedings.neurips.cc/paper_files/paper/2014/file/35f1050a4381d2d216bf56ad46b0277d-Paper.pdf).

For one policy trained across risk settings, let **q** be the training distribution over α. The chosen objective is:

\[
\max_\theta J(\theta),\qquad
J(\theta)=\mathbb{E}_{\alpha\sim q}
\left[\operatorname{CVaR}^{\downarrow}_{\alpha}(G_{\theta,\alpha})\right].
\]

Compute each tail conditional on its risk setting, rather than pooling returns from different α values into one tail. With discrete training settings, use enough rollouts per setting to estimate its threshold η. The same initial-task distribution should be used across α values. Report terrain-specific results as well as the aggregate objective: a tail over all tasks may otherwise consist mostly of one difficult terrain class. Shared policy parameters can also create tradeoffs between risk settings; conditioning does not guarantee that one network matches every separately trained optimum.

### 9.5 Actor updates, distributional critics, and temporal consistency

Start by validating an episodic CVaR estimator on a small stochastic route-choice task. Retain successes and failures. Estimate the return threshold for each α from complete episodes, and update the actor using a CVaR policy-gradient estimator. A distributional critic can estimate a return distribution and its tail; using that critic with an unchanged mean-return actor objective does not implement CVaR optimization.

For clarity, let **τ** denote a complete trajectory, **pθ(τ | α)** its probability under the planner and fixed environment, and **η** the current threshold. At fixed η, the planner gradient of the threshold objective is:

\[
-\frac{1}{\alpha}\mathbb{E}\left[
(\eta-G_{\theta,\alpha})^+
\nabla_\theta\log p_\theta(\tau\mid\alpha)
\right].
\]

For parameter-independent environment dynamics, the log-probability gradient is the sum of the planner's action log-probability gradients along the trajectory. The threshold must also be estimated or optimized; an arbitrary mean-return advantage is not a substitute. This expression describes the objective, not a completed PPO implementation. Any clipped surrogate, baseline, or bootstrapped estimator must be checked against the intended episodic criterion.

A **static episode CVaR objective** evaluates the full return from the start. It is generally not equivalent to applying lower-tail CVaR independently to every state's future return in an ordinary Bellman update. Exact dynamic-programming treatments may augment the state with a risk variable. Our history-conditioned policy with sampled episodes is a policy-search formulation, without a claim of globally optimal Markov control. [Chow et al.](https://papers.neurips.cc/paper_files/paper/2015/file/64223ccf70bbb65a3a4aceac37e21016-Paper.pdf) treat the state-augmentation issue.

[Distributional PPO for quadrupedal locomotion](https://arxiv.org/html/2309.14246v2) uses risk-distorted value estimates in policy updates. It is a useful comparison, but its statewise value distortion must not be presented as an exact optimizer of our static episode-CVaR objective without justification.

Keep α fixed during each initial training episode. Mid-episode changes alter the preference under which future actions are chosen; episode-start CVaR training alone does not guarantee dynamically consistent behavior after such switches. Test switches during stable support first and report the resulting outcomes separately.

### 9.6 When the problem becomes a constrained MDP

A constrained MDP requires an explicit cost and budget. Define **cₜ ≥ 0** as a safety cost and **Cθ,α = Σₜ₌₀ᵀ⁻¹ cₜ** as its undiscounted finite-episode sum. Let **b** be an allowed expected cost. An expected-cost formulation is:

\[
\max_\theta\;\mathbb{E}[G_{\theta,\alpha}]
\quad\text{subject to}\quad
\mathbb{E}[C_{\theta,\alpha}]\le b.
\]

For example, assign cost one at the first fall and zero otherwise. Then C is an episode fall indicator and E[C] is the probability of a fall under the specified task distribution. An undiscounted cost avoids making a late fall count less than an early fall. A different nonnegative cost could measure cumulative excess force or actuator-limit violations, but its units and budget must be specified separately. See [Achiam et al., Constrained Policy Optimization](https://proceedings.mlr.press/v70/achiam17a/achiam17a.pdf).

A tail-cost constraint is another option. Let **β ∈ (0, 1]** denote the fraction of highest-cost episodes and **ζ** a cost threshold. Define upper-tail CVaR by:

\[
\operatorname{CVaR}^{\uparrow}_{\beta}(C)
=\min_{\zeta\in\mathbb{R}}\left\{
\zeta+\frac{1}{\beta}\mathbb{E}[(C-\zeta)^+]
\right\}.
\]

Then replace the expected-cost constraint with **CVaR↑β(Cθ,α) ≤ b**. This is a risk-constrained formulation; a cost-tail constraint is not the same as maximizing lower-tail return. Return-risk preference α, cost-tail fraction β, and budget b have distinct meanings. A risk-sensitive return objective may also be combined with a cost constraint when the task requires both.

A fixed reward penalty for cost is not a constraint. Constrained optimization requires a method that enforces or approximates the stated bound, plus empirical checks of constraint violations. An expected or tail-cost bound under the training distribution does not guarantee safety on every trial or on unseen hardware conditions.

**Chosen scope:** begin with risk-sensitive POMDP policy search using lower-tail episode-return CVaR, without a separate cost constraint. Add a constrained formulation only when the application supplies an explicit cost definition and acceptable budget. Do not describe α as an allowed failure probability.

## 10. Closed-loop behavior to test

An unexpected partial foothold changes the spatial force/torque distribution. The controller should stabilize or replace the foot. At the next planner update, tactile and robot-state history can inform a revised contact target or additional support. This is a separate hypothesis about the interaction between execution and planning; the primary tactile contribution is controller recovery.

The experiment must distinguish a fast corrective action from a changed future strategy. Measure both. Apply the same perturbations to policies with and without tactile observations. For planning, compare tactile input in the controller only against tactile input in both policies.

The risk setting should change the response when alternatives exist. For example, a conservative planner might select a supported crossing or detour after uncertain support; a mean-return planner might accept a faster crossing. These are hypotheses, not predetermined ground-truth behaviors. Hand support itself can be risky when the support surface is slippery, so evaluate outcomes rather than hard-coding a behavior ranking.

## 11. Experiments and metrics

| Experiment | Controlled comparison | Main measurements |
| --- | --- | --- |
| Contact recovery | Same commands and perturbations, tactile input on/off | Contact error, translational slip, foot rotation, recovery time, fall rate |
| Tactile representation | Normal-pressure map; total six-axis wrench; dense three-axis forces; dense six-axis signals; with/without history | Separate spatial, shear-force, torque, and temporal benefits |
| Planner feedback | Tactile controller only versus tactile controller plus planner | Future target changes, support use, success |
| Risk control | Same start, goal, geometry, and disturbance distribution; sweep α | Route/contact choice, time, effort, success, lower-tail return |
| Planner learning | Supervised-only, mean-return RL, risk-conditioned RL | Held-out success and poor outcomes |
| Generalization | Hold out geometry, physical parameters, and obstacle compositions | Per-class performance and recovery |

Contact-position error compares the realized body contact location to its commanded terrain point at contact onset. Track target revisions explicitly. Slip is body contact-point motion relative to the contacted support surface during support; for deformable terrain, account for local surface motion. Define recovery time from perturbation onset to a specified stable-support criterion. Set thresholds before comparing methods.

Report peak contact force and torque about the defined sensor reference point, repeated-trial confidence intervals, and multiple training seeds alongside task success. Evaluate empirical lower-tail returns using enough trials for the selected tail fraction. Also report failure rate at matched completion time or effort where possible, since a slower policy can appear safer without better contact reasoning.

Match observation access, robot limits, source data, procedural terrain exposure, reward terms, and training budget across baselines. Include fixed-risk policies and one policy conditioned on α. Include a reference-free goal-reaching RL baseline. For sensor tests, add delay, dropout, and calibration error deliberately rather than only testing ideal measurements.

## 12. Implementation milestones

1. **Dataset and interface validation.** Replay the existing paired motions and terrains with the selected G1 contact geometry. Validate labels and a contact-command adapter to the mimic controller infrastructure.
2. **Controller and sensing baseline.** Train contact execution on rigid terrain and calibrate the dense six-axis observation model. Demonstrate recovery improvement against matched non-tactile, pressure-map, total-wrench, and dense-force baselines.
3. **Planner initialization.** Record successful controller rollouts, produce hindsight contact targets, and train terrain-point and active-flag prediction. Verify closed-loop navigation before introducing risk learning.
4. **Risk-learning validation.** Validate empirical CVaR on a small route-choice problem, then train the humanoid planner with a frozen controller. Compare against mean-return planning.
5. **Integrated adaptation.** Evaluate tactile history in the planner, alternate controller updates if needed, and test unseen compositions and physical conditions.
6. **Hardware.** Begin with available G1 hardware and calibrated foot sensors. Show recovery and changed contact strategy on the same course. A full-size humanoid demonstration remains a later target contingent on hardware and sensor access.

Compliant and granular contact experiments follow rigid-terrain validation. Direct hand-tactile claims follow hand-sensor integration. These extensions must not block the first clean tests of foot-feedback recovery and risk-conditioned contact choice.

## 13. Success criteria

The first contribution requires statistically supported recovery gains beyond normal-pressure-map and total-six-axis-wrench baselines, plus an ablation against dense three-axis force sensing, with a matched sensing and control setup on hardware. The second requires repeatable contact or route changes under the risk command, together with measured improvement of poor outcomes and an explicit time or energy tradeoff. A separate integrated extension can test whether tactile evidence improves later planning decisions; do not make that claim without the corresponding ablation.

If tactile input only reduces touchdown force, narrow the claim to that outcome. If risk only changes speed, do not claim contact-strategy control. If improvements only occur on demonstrated terrain, do not claim generalization to novel combinations. These criteria determine whether the proposed story is supported by experiments.
