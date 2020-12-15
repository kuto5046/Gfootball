from matplotlib import animation, patches, rcParams
from matplotlib import pyplot as plt
from kaggle_environments.envs.football.helpers import *

# WIDTH = 110
# HEIGHT = 46.2
# PADDING = 10
WIDTH = 105
HEIGHT = 68
PADDING = 10

def initFigure(figwidth=12):
    figheight = figwidth * (HEIGHT + 2 * PADDING) / (WIDTH + 2 * PADDING)

    fig = plt.figure(figsize=(figwidth, figheight))
    ax = plt.axes(xlim=(-PADDING, WIDTH + PADDING), ylim=(-PADDING, HEIGHT + PADDING))
    plt.axis("off")
    return fig, ax


def drawPitch(ax):
    paint = "white"

    # Grass around pitch
    rect = patches.Rectangle((-PADDING / 2, -PADDING / 2), WIDTH + PADDING, HEIGHT + PADDING,
                             lw=1, ec="black", fc="#3f995b", capstyle="round")
    ax.add_patch(rect)

    # Pitch boundaries
    rect = plt.Rectangle((0, 0), WIDTH, HEIGHT, ec=paint, fc="None", lw=2)
    ax.add_patch(rect)

    # Middle line
    plt.plot([WIDTH / 2, WIDTH / 2], [0, HEIGHT], color=paint, lw=2)

    # Dots
    dots_x = [11, WIDTH / 2, WIDTH - 11]
    for x in dots_x:
        plt.plot(x, HEIGHT / 2, "o", color=paint, lw=2)

    # Penalty box
    penalty_box_dim = [16.5, 40.3]
    penalty_box_pos_y = (HEIGHT - penalty_box_dim[1]) / 2

    rect = plt.Rectangle((0, penalty_box_pos_y),
                         penalty_box_dim[0], penalty_box_dim[1], ec=paint, fc="None", lw=2)
    ax.add_patch(rect)
    rect = plt.Rectangle((WIDTH, penalty_box_pos_y), -
                         penalty_box_dim[0], penalty_box_dim[1], ec=paint, fc="None", lw=2)
    ax.add_patch(rect)

    # Goal box
    goal_box_dim = [5.5, penalty_box_dim[1] - 11 * 2]
    goal_box_pos_y = (penalty_box_pos_y + 11)

    rect = plt.Rectangle((0, goal_box_pos_y),
                         goal_box_dim[0], goal_box_dim[1], ec=paint, fc="None", lw=2)
    ax.add_patch(rect)
    rect = plt.Rectangle((WIDTH, goal_box_pos_y),
                         -goal_box_dim[0], goal_box_dim[1], ec=paint, fc="None", lw=2)
    ax.add_patch(rect)

    # Goals
    goal_width = 0.044 / 0.42 * HEIGHT
    goal_pos_y = (HEIGHT / 2 - goal_width / 2)
    rect = plt.Rectangle((0, goal_pos_y), -2, goal_width,
                         ec=paint, fc=paint, lw=2, alpha=0.3)
    ax.add_patch(rect)
    rect = plt.Rectangle((WIDTH, goal_pos_y), 2, goal_width,
                         ec=paint, fc=paint, lw=2, alpha=0.3)
    ax.add_patch(rect)

    # Middle circle
    mid_circle = plt.Circle([WIDTH / 2, HEIGHT / 2], 9.15, color=paint, fc="None", lw=2)
    ax.add_artist(mid_circle)

    # Penalty box arcs
    left = patches.Arc([11, HEIGHT / 2], 2 * 9.15, 2 * 9.15,
                       color=paint, fc="None", lw=2, angle=0, theta1=308, theta2=52)
    ax.add_patch(left)
    right = patches.Arc([WIDTH - 11, HEIGHT / 2], 2 * 9.15, 2 * 9.15,
                        color=paint, fc="None", lw=2, angle=180, theta1=308, theta2=52)
    ax.add_patch(right)

    # Arcs on corners
    corners = [[0, 0], [WIDTH, 0], [WIDTH, HEIGHT], [0, HEIGHT]]
    angle = 0
    for x, y in corners:
        c = patches.Arc([x, y], 2, 2,
                        color=paint, fc="None", lw=2, angle=angle, theta1=0, theta2=90)
        ax.add_patch(c)
        angle += 90


def scale_x(x):
    return (x + 1) * (WIDTH / 2)


def scale_y(y):
    return (y + 0.42) * (HEIGHT / 0.42 / 2)


def extract_data(raw_obs):
    obs = raw_obs[0]["observation"]["players_raw"][0]
    res = dict()
    res["left_team"] = [(scale_x(x), scale_y(y)) for x, y in obs["left_team"]]
    res["right_team"] = [(scale_x(x), scale_y(y)) for x, y in obs["right_team"]]

    ball_x, ball_y, ball_z = obs["ball"]
    res["ball"] = [scale_x(ball_x), scale_y(ball_y), ball_z]
    res["score"] = obs["score"]
    res["steps_left"] = obs["steps_left"]
    res["ball_owned_team"] = obs["ball_owned_team"]

    left_active = raw_obs[0]["observation"]["players_raw"][0]["active"]
    res["left_player"] = res["left_team"][left_active]

    right_active = raw_obs[1]["observation"]["players_raw"][0]["active"]
    res["right_player"] = res["right_team"][right_active]

    res["right_team_roles"] = obs["right_team_roles"]
    res["left_team_roles"] = obs["left_team_roles"]
    res["left_team_direction"] = obs["left_team_direction"]
    res["right_team_direction"] = obs["right_team_direction"]
    res["game_mode"] = GameMode(obs["game_mode"]).name
    return res


def draw_team(obs, team, side):
    x_coords, y_coords = zip(*obs[side])
    team.set_data(x_coords, y_coords)


def draw_ball(obs, ball):
    ball.set_markersize(8 + obs["ball"][2])  # Scale size of ball based on height
    ball.set_data(obs["ball"][:2])


def draw_active_players(obs, left_player, right_player):
    x1, y1 = obs["left_player"]
    left_player.set_data(x1, y1)

    x2, y2 = obs["right_player"]
    right_player.set_data(x2, y2)

    if obs["ball_owned_team"] == 0:
        left_player.set_markerfacecolor("yellow")
        left_player.set_markersize(20)
        right_player.set_markerfacecolor("blue")
        right_player.set_markersize(18)
    elif obs["ball_owned_team"] == 1:
        left_player.set_markerfacecolor("firebrick")
        left_player.set_markersize(18)
        right_player.set_markerfacecolor("yellow")
        right_player.set_markersize(20)
    else:
        left_player.set_markerfacecolor("firebrick")
        left_player.set_markersize(18)
        right_player.set_markerfacecolor("blue")
        right_player.set_markersize(18)


def draw_team_active(obs, team_left_active, team_right_active):
    team_left_active.set_data(WIDTH / 2 - 7, -7)
    team_right_active.set_data(WIDTH / 2 + 7, -7)

    if obs["ball_owned_team"] == 0:
        team_left_active.set_markerfacecolor("indianred")
    else:
        team_left_active.set_markerfacecolor("mistyrose")

    if obs["ball_owned_team"] == 1:
        team_right_active.set_markerfacecolor("royalblue")
    else:
        team_right_active.set_markerfacecolor("lightcyan")


def draw_players_directions(obs, directions, side):
    index = 0
    if "right" in side:
        index = 11
    for i, player_dir in enumerate(obs[f"{side}_direction"]):
        x_dir, y_dir = player_dir
        dist = (x_dir ** 2 + y_dir ** 2)**0.5 + 0.00001  # to prevent division by 0
        x = obs[side][i][0]
        y = obs[side][i][1]
        directions[i + index].set_data([x, x + x_dir / dist], [y, y + y_dir / dist])


def player_actions(step, side):
    if side == 0:
        actions = {0: "idle", 1: "←", 2: "↖", 3: "↑", 4: "↗", 5: "→", 6: "↘", 7: "↓", 8: "↙",
                   9: "l_pass", 10: "h_pass", 11: "s_pass", 12: "shot",
                   13: "sprint", 14: "rel_dir", 15: "rel_spr",
                   16: "slide", 17: "dribble", 18: "stp_drb"}
    else:
        actions = {0: "idle", 1: "→", 2: "↘", 3: "↓", 4: "↙", 5: "←", 6: "↖", 7: "↑", 8: "↗",
                   9: "l_pass", 10: "h_pass", 11: "s_pass", 12: "shot",
                   13: "sprint", 14: "rel_dir", 15: "rel_spr",
                   16: "slide", 17: "dribble", 18: "stp_drb"}

    obs = step[side]["observation"]["players_raw"][0]

    if obs["sticky_actions"][8]:
        spr = "+spr"
    else:
        spr = "-spr"

    if obs["sticky_actions"][9]:
        drb = "+drb"
    else:
        drb = "-drb"

    if 1 in obs["sticky_actions"][0:8]:
        i = obs["sticky_actions"][0:8].index(1) + 1
        drn = actions[i]
    else:
        drn = "|"

    if step[side]["action"]:
        act = actions[step[side]["action"][0]]
    else:
        act = "idle"

    return f"{spr} {drb} {drn} [{act}]".ljust(24, " ")


steps = None
drawings = None
directions = None
ball = left_player = right_player = None
team_left = team_right = None
team_left_active = team_right_active = None
team_left_actions = team_right_actions = None
team_left_number = team_right_number = None
team_left_direction = team_right_direction = None
text_frame = game_mode = match_info = None


def init():
    ball.set_data([], [])
    left_player.set_data([], [])
    right_player.set_data([], [])
    team_left.set_data([], [])
    team_right.set_data([], [])
    team_left_active.set_data([], [])
    team_right_active.set_data([], [])
    return drawings


def animate(i):
    obs = extract_data(steps[i])

    # Draw info about ball possesion
    draw_active_players(obs, left_player, right_player)
    draw_team_active(obs, team_left_active, team_right_active)

    # Draw players
    draw_team(obs, team_left, "left_team")
    draw_team(obs, team_right, "right_team")

    draw_players_directions(obs, directions, "left_team")
    draw_players_directions(obs, directions, "right_team")

    draw_ball(obs, ball)

    # Draw textual informations
    text_frame.set_text(f"Step {i}/{obs['steps_left'] + i - 1}")
    game_mode.set_text(f"{obs['game_mode']} Mode")

    score_a, score_b = obs["score"]
    match_info.set_text(f"{score_a} : {score_b}")

    team_left_actions.set_text(player_actions(steps[i], 0))
    team_right_actions.set_text(player_actions(steps[i], 1))

    team_left_number.set_text(str(steps[i][0]["observation"]["players_raw"][0]["active"]))
    team_right_number.set_text(str(steps[i][1]["observation"]["players_raw"][0]["active"]))

    return drawings


def visualize(trace):
    global steps
    global drawings
    global directions
    global ball, left_player, right_player
    global team_left, team_right
    global team_left_active, team_right_active
    global text_frame, game_mode, match_info
    global team_left_actions, team_right_actions
    global team_left_number, team_right_number
    global team_left_direction, team_right_direction

    rcParams['font.family'] = 'monospace'
    rcParams['font.size'] = 12

    steps = trace

    fig, ax = initFigure()
    drawPitch(ax)
    ax.invert_yaxis()

    left_player, = ax.plot([], [], "o", ms=18, mfc="firebrick", mew=0, alpha=0.5)
    right_player, = ax.plot([], [], "o", ms=18, mfc="blue", mew=0, alpha=0.5)
    team_left, = ax.plot([], [], "o", ms=12, mfc="firebrick", mew=1, mec="white")
    team_right, = ax.plot([], [], "o", ms=12, mfc="blue", mew=1, mec="white")
    ball, = ax.plot([], [], "o", ms=8, mfc="wheat", mew=1, mec="black")

    team_left_active, = ax.plot([], [], "o", ms=16, mfc="mistyrose", mec="None")
    team_right_active, = ax.plot([], [], "o", ms=16, mfc="lightcyan", mec="None")

    textheight = -6
    text_frame = ax.text(-5, textheight, "", ha="left")
    match_info = ax.text(WIDTH / 2, textheight, "", ha="center", fontweight="bold")
    game_mode = ax.text(WIDTH + 5, textheight, "", ha="right")

    team_left_actions = ax.text(WIDTH / 4 + 2, textheight, "", ha="center")
    team_right_actions = ax.text(3 * WIDTH / 4 + 2, textheight, "", ha="center")

    team_left_number = ax.text(WIDTH / 2 - 7, -6.3, "", ha="center", fontsize=10)
    team_right_number = ax.text(WIDTH / 2 + 7, -6.3, "", ha="center", fontsize=10)

    # Drawing of directions definitely can be done in a better way
    directions = []
    for _ in range(22):
        direction, = ax.plot([], [], color="yellow", lw=1.5)
        directions.append(direction)

    drawings = [team_left_active, team_right_active, left_player, right_player,
                team_left, team_right, ball, text_frame, match_info,
                game_mode, team_left_actions, team_right_actions, team_left_number, team_right_number]

    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
    anim = animation.FuncAnimation(fig, animate, init_func=init, blit=True,
                                   interval=100, frames=len(steps), repeat=True)
    return anim
