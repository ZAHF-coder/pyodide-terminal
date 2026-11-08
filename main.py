import pygame
import pymunk
import pymunk.pygame_util  # Allows pymunk to use pygame to draw
import math
import asyncio


async def main():

    pygame.init()   # Initialises pygame

    WIDTH, HEIGHT = 1000,500 # The size of the pygame window
    window1 = pygame.display.set_mode((WIDTH, HEIGHT)) # pygame window - where the simulation will be displayed  
        
    def distance():
        start_pos = (20,480)
        mouse_pos = pygame.mouse.get_pos() # uses mouse position
        dx = mouse_pos[0] - start_pos[0]
        dy = mouse_pos[1] - start_pos[1]
        rad= round((math.sqrt(dx**2+dy**2))/100,2)
        return rad

    def angle_rad():
        start_pos = (20,480)
        mouse_pos = pygame.mouse.get_pos() # uses mouse position
        dx = mouse_pos[0] - start_pos[0]
        dy = mouse_pos[1] - start_pos[1]
        theta1 = math.atan2(-dy,dx)
        return theta1

    def angle_deg():
        theta2 = round(math.degrees(angle_rad()))
        return theta2
            
    def launch(velocity):
        moment = pymunk.moment_for_circle(20, 0, 8)
        body = pymunk.Body(20, moment, body_type=pymunk.Body.DYNAMIC) # creating a body
        body.position =  (20,480) 
        body.velocity = velocity # setting initial velocity that the ball will be lauched at
        shape = pymunk.Circle(body,10) # creating a shape for the body
        shape.collision_type = 1 
        """shape.friction = 0.5"""
        shape.color = (250,0,0,0) # RGBA value
        space.add(body, shape) # attaching the shape to the body
        return shape

    def draw(space, window1,options):
        window1.fill("light blue") #clears the window - background colour blue
        for x in range(0,1000, 10): # 100 lines
            pygame.draw.line(window1, "Blue", (x, 0), (x, 500)) # Vertical lines
        for y in range(0, 500, 10): # 50 lines
            pygame.draw.line(window1, "Blue", (0, y), (1000, y)) # Horizontal lines
        mouse_pos = pygame.mouse.get_pos() # uses mouse position   
        pygame.draw.line(window1,"Black",(20,480),mouse_pos,3)
        start_pos = (20,480)
        mouse_pos = pygame.mouse.get_pos() # uses mouse position
        pygame.draw.line(window1,"Dark Green",start_pos,(mouse_pos[0],480),4)
        mos_x = mouse_pos[0]-10
        pygame.draw.line(window1,"Dark Green",(mouse_pos[0],480),(mos_x,470),4)
        pygame.draw.line(window1,"Dark Green",(mouse_pos[0],480),(mos_x,490),4)
        pygame.draw.line(window1,"Orange",start_pos,(20,mouse_pos[1]),4)
        mos_y = mouse_pos[1]+10
        pygame.draw.line(window1,"Orange",(20,mouse_pos[1]),(10,mos_y),4)
        pygame.draw.line(window1,"Orange",(20,mouse_pos[1]),(30,mos_y),4)
        r=distance()
        font = pygame.font.Font(None, 30)
        text = font.render("Launch Vector: " +str(r)+"m",True, pygame.Color("black"))
        window1.blit(text, (20, 35))
        theta2=angle_deg()
        text = font.render("Launch Angle: "+str(theta2)+"\N{DEGREE SIGN}",True, pygame.Color("black"))
        window1.blit(text, (20, 15))
        if calcs is not None:
            velocity2, H, d, t = calcs
            text = font.render("Velocity: "+str(round(velocity2,2))+"m/s",True, pygame.Color("black"))
            window1.blit(text, (740, 15))     
            text = font.render("Maximum Height: "+str(H)+"m",True, pygame.Color("black"))
            window1.blit(text, (740, 35))     
            text = font.render("Distance Range: "+str(d)+"m",True, pygame.Color("black"))
            window1.blit(text, (740, 55))     
            text = font.render("Time: "+str(t)+"s",True, pygame.Color("black"))
            window1.blit(text, (740, 75))
        space.debug_draw(options)
        
    def boundaries(space, width, height):
        rects = [
            [(width/2,height-5),(width,10)],
            [(width/2,5),(width,10)],
            [(5,height/2),(10,height)],
            [(width-5,height/2),(10,height)]
        ]

        for position, size in rects:
            body=pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = position
            rec = pymunk.Poly.create_box(body, size)
            rec.collision_type = 2
            rec.color=(0,0,255,100) # RGBA 
            """rec.elasticity = 0.5
            rec.friction = 0.5"""
            space.add(body,rec)

    collision_occurred = False

    def collision_detection(arbiter, space, data):
        global collision_occurred
        collision_occurred = True
        return collision_occurred
      
    """def removal(arbiter, space, data):
        shape_a, shape_b = arbiter.shapes
        for p in projections:
            canon = p["canons"]
            if canon == shape_a or canon == shape_b:
                space.remove(canon,canon.body)
        return True"""
    def removal(arbiter, space, data):
        shape_a, shape_b = arbiter.shapes

        for p in projections[:]:
            canon = p["canons"]

            if canon == shape_a or canon == shape_b:
                space.remove(canon, canon.body)
                projections.remove(p)

        return True


    clock = pygame.time.Clock()
    fps = 30
    dt = 1 / fps
        
    space = pymunk.Space()      # Create a Space which contain the simulation

    space.gravity = (0,981)# Set its gravity - this value can be anything

    boundaries(space, 1000, 500)

    options = pymunk.pygame_util.DrawOptions(window1)

    projections = []
    space.on_collision(1, 2, begin=removal)# removes the ball when it touches the boundaries

    class Projectile: # OOP 
        def __init__(self, velocity,angle):
            # Attributes = state
            self.velocity = velocity
            self.angle = angle
            self.g=9.81
            self.distance_travelled = 0 + abs(self.range())
        
        def time(self):
            return round((2 * self.velocity * math.sin(self.angle)) / self.g, 2)

        def range(self):
            range_ = ((self.velocity ** 2) * math.sin(2*self.angle)) / self.g
            return round(range_, 2)

        def max_height(self):
            h = ((self.velocity ** 2) * (math.sin(self.angle)) ** 2) / (2 * self.g)
            return round(h, 2)

    def trajectories(projectiles):
        for p in projectiles:
            position = p["canons"].body.position # Store the ball's current position
            p["path"].append((int(position.x), int(position.y)))

    def draw_trajectories(window, projectiles):
        for p in projectiles:
            trail = p["path"]
            if len(trail) > 1:
                pygame.draw.lines(window,(255, 0, 0),False,trail,2)
     
    calcs = None

    run1 = True    
    while run1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Quits the window
                run1 = False
                break
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                start_pos = (20,480)
                mouse_pos = pygame.mouse.get_pos() # uses mouse position
                dx = mouse_pos[0] - start_pos[0]
                
                dy = mouse_pos[1] - start_pos[1]
                v = (dx*2,dy*2)
                canon=launch(v)
                velocity1= math.sqrt((dx*2)**2+(dy*2)**2)
                velocity2 = velocity1/100 # converting from pixels to "metres" using 100 pixels = 1 metre
                angle = angle_rad()
                projectile = Projectile(velocity2,angle) # thoretical calculations
                H=projectile.max_height()
                t=projectile.time()
                d=projectile.range()
                calcs = (velocity2, H, d, t)
                projections.append({ # Dictionary
                "canons":canon,
                "calculations":projectile,
                "path":[]
                })
            if event.type == pygame.KEYDOWN:
                projections.clear()
            
                
        pygame.display.set_caption("Click the DOWN ARROW KEY to clear all paths!")
        space.step(dt)
        trajectories(projections)
        draw(space,window1,options)
        
        draw_trajectories(window1, projections)
        pygame.display.flip()
        await asyncio.sleep(1 / fps)

    pygame.quit()
asyncio.create_task(main())

