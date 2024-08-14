import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def fetchcsv():
    df = pd.read_csv(r"C:\Users\Lenovo\SA\sa_project.csv")
    df = df.set_index('POINT')
    return df

def writecsv(df):
    df.to_csv(r"C:\Users\Lenovo\SA\sa_project.csv", na_rep="NULL")

def showcsv(df):
    print(df)

def addpoints(df):
    POINT = input("Enter point: ")
    X_AXIS = int(input("Enter x value: "))
    Y_AXIS = int(input("Enter y value: ")) 
    H_LOAD = int(input("Enter horizontal force: "))
    V_LOAD = int(input("Enter vertical force: "))
    df.loc[POINT] = [X_AXIS, Y_AXIS, H_LOAD, V_LOAD]
    print(df)
    writecsv(df)

def distance(df, point1, point2):
    x1, y1 = df.loc[point1, 'X-AXIS'], df.loc[point1, 'Y-AXIS']
    x2, y2 = df.loc[point2, 'X-AXIS'], df.loc[point2, 'Y-AXIS']
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def define_connections(df):
    nodes = df[['X-AXIS', 'Y-AXIS']].values
    connections = []
    for i in range(len(nodes) - 1):
        connections.append((i, i + 1))
    # Add connection between the first and last point to close the loop
    connections.append((0, len(nodes) - 1))
    return connections

def calculate_coefficient(df, point, ref_point):
    # Fetch force components at the specified point
    force_x_1 = df.loc[point, 'H_LOAD']
    force_y_1 = df.loc[point, 'V_LOAD']
    force_x_2 = df.loc[ref_point, 'H_LOAD']
    force_y_2 = df.loc[ref_point, 'V_LOAD']
    
    # Calculate total horizontal and vertical forces
    total_horizontal_force = force_x_1 + force_x_2
    total_vertical_force = force_y_1 + force_y_2
    
    # Fetch coordinates of the specified point and reference point
    x_point, y_point = df.loc[point, ['X-AXIS', 'Y-AXIS']]
    x_ref, y_ref = df.loc[ref_point, ['X-AXIS', 'Y-AXIS']]
    
    # Calculate perpendicular distance between the two points
    distance = np.sqrt((x_ref - x_point) ** 2 + (y_ref - y_point) ** 2)
    
    # Calculate moment
    moment = total_horizontal_force * (y_ref - y_point) - total_vertical_force * (x_ref - x_point)
    
    # Calculate coefficient
    if distance == 0:
        coefficient = 0  # Avoid division by zero
    else:
        coefficient = moment / distance
    
    return coefficient

def calculate_member_forces(df):
    # Initialize member forces list
    member_forces = []
    
    # Get the list of points
    points = df.index.tolist()
    
    # Iterate over each point except the last one
    for i in range(len(points) - 1):
        point1 = points[i]
        point2 = points[i + 1]
        
        # Calculate the distance between two points
        length = np.sqrt((df.loc[point2, 'X-AXIS'] - df.loc[point1, 'X-AXIS']) ** 2 + 
                         (df.loc[point2, 'Y-AXIS'] - df.loc[point1, 'Y-AXIS']) ** 2)
        
        # Calculate total horizontal and vertical forces at each joint
        total_horizontal_force = df.loc[point1, 'H_LOAD'] + df.loc[point2, 'H_LOAD']
        total_vertical_force = df.loc[point1, 'V_LOAD'] + df.loc[point2, 'V_LOAD']
        
        # Calculate the angle of the member
        theta = np.arctan2(df.loc[point2, 'Y-AXIS'] - df.loc[point1, 'Y-AXIS'],
                           df.loc[point2, 'X-AXIS'] - df.loc[point1, 'X-AXIS'])
        
        # Calculate the member force components
        member_force_x = total_horizontal_force * np.cos(theta) + total_vertical_force * np.sin(theta)
        member_force_y = total_vertical_force * np.cos(theta) - total_horizontal_force * np.sin(theta)
        
        # Calculate the net member force magnitude
        net_force = np.sqrt((member_force_x) ** 2 + (member_force_y) ** 2)
        
        # Append the net member force to the list
        member_forces.append((member_force_x, member_force_y))
    
    return member_forces

# Example usage:
df = fetchcsv()
member_forces = calculate_member_forces(df)
print("Member forces:", member_forces)

# Plot truss diagram with member forces
connections = define_connections(df)
nodes = df[['X-AXIS', 'Y-AXIS']].values

plt.figure(figsize=(8, 6))
for i, (x, y) in enumerate(nodes):
    plt.plot(x, y, 'ko')
    plt.text(x, y, f'P{i+1}', fontsize=12, ha='right', va='bottom')

for (i, j) in connections:
    x1, y1 = nodes[i]
    x2, y2 = nodes[j]
    plt.plot([x1, x2], [y1, y2], 'b-', linewidth=1)

plt.xlabel('X')
plt.ylabel('Y')
plt.title('Truss Diagram')
plt.grid(True)
plt.axis('equal')

# Plot member forces
for (i, j), (force_x, force_y) in zip(connections, member_forces):
    (x1, y1), (x2, y2) = nodes[i], nodes[j]
    xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
    plt.text(xm, ym, f'({force_x:.2f}, {force_y:.2f})', fontsize=10, ha='center', va='center')

plt.show()