from random import shuffle
from visualization import *

class Triangulation:

    def __init__(self):
        self.triangles = set()
        self.edges_map = {}
        self.outer_triangle = None
        self.centeral_triangle = None
    

    def add_triangle(self, triangle):
        triangle = self.sort_triangle_vertices(triangle)
        
        self.triangles.add(triangle)
        
        a, b, c = triangle
        self.edges_map[(a, b)] = c
        self.edges_map[(b, c)] = a
        self.edges_map[(c, a)] = b


    def remove_triangle(self, triangle):
        triangle = self.sort_triangle_vertices(triangle)
        
        self.triangles.remove(triangle)
        
        a, b, c = triangle
        del self.edges_map[(a, b)]
        del self.edges_map[(b, c)]
        del self.edges_map[(c, a)]


    def sort_triangle_vertices(self, triangle):
        a, b, c = triangle
        
        if det_sgn(a,b,c) == -1:
            a, b = b, a

        while(a[1] > min(b[1], c[1])
              or (a[1] == min(b[1], c[1]) and a[1] != b[1])):
            a, b, c = b, c, a
            
        return (a, b, c)


    def make_outer_triangle(self, points):
        '''
        dodanie do triangulacji tymczasowego duzego trójkąta, który zawiera wszystkie punkty
        '''
        max_coord = abs(max(points, key = lambda x: abs(x[0]))[0])
        max_coord = max(max_coord, abs(max(points, key = lambda x: abs(x[1]))[1]))

        self.outer_triangle = ((3*max_coord, 0), (0, 3*max_coord), (-3*max_coord, -3*max_coord))
        self.add_triangle(self.outer_triangle)

        self.central_triangle = self.outer_triangle

        
    def triangle_containing(self, point):
        '''
        zwraca trójkąt, w którym lezy punkt, ewentualnie lezy na brzegu
        '''
        current = self.central_triangle

        while True:
            a, b, c = current
            if det_sgn(a, b, point) == -1:
                current = self.triangle_adjacent((a,b))
            elif det_sgn(b, c, point) == -1:
                current = self.triangle_adjacent((b,c))
            elif det_sgn(c, a, point) == -1:
                current = self.triangle_adjacent((c,a))
            else:
                return current
                

    def triangle_adjacent(self, edge):
        '''
        zwraca trójkąt przyległy do 'triangle' o wspólnej krawędzi edge
        zakłada, ze edge jest krawędzią skierowaną zgodną z kierunkiem trójkąta
        przeciwnym do ruchu wskazówek zegara
        '''
        if (edge[1], edge[0]) in self.edges_map:
            return self.sort_triangle_vertices((edge[1], edge[0], self.edges_map(edge[1], edge[0])))
        
        return None


    def all_triangles_adjacent(self, triangle):
        triangles = []
        a, b, c = triangle

        triangle_adjacent = self.triangle_adjacent((a,b))
        if triangle_adjacent:
            triangles.append(triangle_adjacent)

        triangle_adjacent = self.triangle_adjacent((b,c))
        if triangle_adjacent:
            triangles.append(triangle_adjacent)

        triangle_adjacent = self.triangle_adjacent((c,a))
        if triangle_adjacent:
            triangles.append(triangle_adjacent)
        
        return triangles


    def split_triangle(self, triangle, point):
        '''
        podział trójkąta w przypadku, gdy nowy punkt lezy wewnątrz
        '''
        triangle1 = point, triangle[0], triangle[1]
        triangle2 = point, triangle[1], triangle[2]
        triangle3 = point, triangle[0], triangle[2]
        
        self.remove_triangle(triangle)
        
        self.add_triangle(triangle1)
        self.add_triangle(triangle2)
        self.add_triangle(triangle3)
        

    def split_triangle_on_edge(self, edge, point):
        '''
        podział trójkątów, gdy nowy punkt lezy na krawędzi
        '''
        ver1, ver2 = edge
        edge1 = ver1, ver2
        edge2 = ver2, ver1
        
        triangle1 = point, ver1, self.third_vertex(edge1)
        triangle2 = point, ver2, self.third_vertex(edge2)
        triangle3 = point, ver1, self.third_vertex(edge1)
        triangle4 = point, ver2, self.third_vertex(edge2)

        self.remove_triangle((ver1, ver2, self.third_vertex(edge1)))
        self.remove_triangle((ver1, ver2, self.third_vertex(edge2)))

        self.add_triangle(triangle1)
        self.add_triangle(triangle2)
        self.add_triangle(triangle3)
        self.add_triangle(triangle4)
        

    def remove_outer(self):
        '''
        usunięcię wszystkich trójkątów, które zawierają dodane na początku wierzchołki duzego trójkąta
        '''

        outer_vertices = set(self.outer_triangle)
        triangles = list(self.triangles)

        for triangle in triangles:
            if not triangle[0] in outer_vertices and not triangle[1] in outer_vertices and not triangle[2] in outer_vertices:
                continue

            self.remove_triangle(triangle)

        
    def is_illegal(self, edge):
        '''
        czworokąt abcd o przekątnej edge
        '''

        b, c = edge
        a = self.edges_map[edge]
        d = self.edges_map[(c, b)]

        outer_vertices = set(self.outer_triangle)
        if a in outer_vertices or b in outer_vertices or c in outer_vertices or d in outer_vertices:
            return self.is_illegal_outer(edge)

        return not self.is_within_circumcircle((a,b,c), d)


    def is_illegal_outer(self, edge):

        b, c = edge
        a = self.edges_map[edge]
        d = self.edges_map[(c, b)]

        def outer_triangle_index(x):
            v1 = max(self.outer_triangle, key=lambda x: x[0])
            v2 = max(self.outer_triangle, key=lambda x: x[1])
            v3 = min(self.outer_triangle, key=lambda x: x[0])

            if x == v1: return -1
            if x == v2: return -2
            if x == v3: return -3
            return 0

        indices = list(map(outer_triangle_index, [a, b, c, d]))
        is_outer = list(map(lambda x: x<0, indices))

        if is_outer[1] and is_outer[2]:
            return False

        if is_outer == [False, True, False, False] or is_outer == [False, False, True, False]:
            return True

        if (not is_outer[0] and is_outer[3]) or (is_outer[0] and not is_outer[3]):
            return False
        
        negative_index_a_d = min(indices[0], indices[3])
        negative_index_b_c = min(indices[1], indices[2])

        return negative_index_b_c > negative_index_a_d



    def legalize_edge(self, point, edge):
        if self.is_illegal(edge):
            a, b = edge
            if(self.third_vertex(edge) != point):
                a, b = b, a
            c = self.third_vertex((b,a)) 
            
            self.delete_triangle((a,b,point))
            self.delete_triangle((a,b,c))

            self.add_triangle((a, point, c))
            self.add_triangle((b, point, c))

            self.legalize_edge(point, (a, c))
            self.legalize_edge(point, (b, c))

    
    def edge_with_point(self, point, triangle):
        a, b, c = triangle
        
        if detSgn(a, b, point) == 0:
            return (a, b)
        if detSgn(b, c, point) == 0:
            return (b, c)
        if detSgn(c, a, point) == 0:
            return (c, a)
        return None


    def third_vertex(self, edge):
        '''
        zwraca wierzchołek trójkąta, który nie nalezy do edge
        '''
        return self.edges_map(edge)


<<<<<<< HEAD
    def dist(self, point_1, point_2):
        '''
        odległość euklidesowa punktów point_1 i point_2
        '''
        return ((point_2[0]-point_1[0])**2 + (point_2[1]-point_1[1])**2)**0.5
=======
>>>>>>> 5f5820a2040e69915c38069ccc8e7bdaa86bd853


    def find_circumcircle(self, triangle):
        '''
        zwraca środek i promień okręgu opisanego na trójkącie triangle
        wzorki z wikipedii
        '''
        a, b, c = triangle
        
        d = 2*(a[0]*(b[1]-c[1])+b[0]*(c[1]-a[1])+c[0]*(a[1]-b[1]))
        
        x = ((a[0]**2 + a[1]**2)*(b[1]-c[1]) 
            + (b[0]**2 + b[1]**2)*(c[1]-a[1])
            + (c[0]**2 + c[1]**2)*(a[1]-b[1]))/d

        y = ((a[0]**2 + a[1]**2)*(c[0]-b[0]) 
            + (b[0]**2 + b[1]**2)*(a[0]-c[0])
            + (c[0]**2 + c[1]**2)*(b[0]-a[0]))/d

        return (x, y), dist((x,y), a)


    def is_within_circumcircle(self, triangle, point):
        '''
        TODO: dodać tolerancję?
        '''
        circumcenter, radius = self.find_circumcircle(triangle)
        
        dist_to_center = dist(point, circumcenter)
        return dist_to_center <= radius


    def remove_and_connect(self, triangles_to_remove, point_to_add):
        points = set()

        for triangle in triangles_to_remove:
            points.add(triangle[0])
            points.add(triangle[1])
            points.add(triangle[2])
            self.remove_triangle(triangle)
        
        points = list(points)
        sort_points(points, point_to_add, 0, len(points)-1)

        for i in range(len(points)):
            self.add_triangle((point_to_add, points[i], points[i-1]))


tolerance = 10**(-12)

def det_sgn(a, b, c):
    l1 = a[0]*b[1]
    l2 = a[1]*c[0]
    l3 = b[0]*c[1]
    r1 = b[1]*c[0]
    r2 = a[0]*c[1]
    r3 = a[1]*b[0]

    value = (l1 + l2 + l3) - (r1 + r2 + r3)

    if value > tolerance:
        return 1
    if value < -tolerance:
        return -1
    return 0


def dist(point_1, point_2):
    '''
    odległość euklidesowa punktów point_1 i point_2
    '''
    return ((point_2[0]-point_1[0])**2 + (point_2[1]-point_1[1])**2)**0.5


def sort_points(t, p0, a, b):  
    '''
    t -> tablica do posortowania (modyfikuje przekazaną tablicę)
    p0 -> punkt względem którego sortujemy
    a, b -> liczby naturalne określające przedział aktualnie sortowany
    '''
    
    pivot = t[b]
    i = a

    for j in range(a, b):
        if det_sgn(p0, t[j], pivot) == 1:
            t[i], t[j] = t[j], t[i]
            i += 1

    t[b], t[i] = t[i], t[b]
    if i > a: sort_points(t, p0, a, i-1)
    if i < b: sort_points(t, p0, i+1, b)


def delaunay_triangulation(points):
    '''
    główna funkcja do triangulacji w pierwszym wariancie
    na podstawie pseudokodu z ksiązki de Berga
    '''
    triangulation = Triangulation()
    triangulation.make_outer_triangle(points)

    shuffle(points)

    for point in points:
        triangle_containing = triangulation.triangle_containing(point)

        if not triangle_containing.is_on_edge(point): # punkt wewnątrz trójkąta
            triangulation.split_triangle(triangle_containing, point)
            i, j, k = triangle_containing
            triangulation.legalize_edge(point, (i, j))
            triangulation.legalize_edge(point, (j, k))
            triangulation.legalize_edge(point, (k, i))

        else: # punkt na brzegu trójkąta
            i, j = triangle_containing.edge_with_point(point)
            triangle_adjacent = triangulation.triangle_adjacent((i, j))
            l = triangulation.third_vertex((i, j))

            triangulation.split_triangle_on_edge(triangle_containing, (i,j), point)
            triangulation.split_triangle_on_edge(triangle_adjacent, (i,j), point)

            triangulation.legalize_edge(point, (i, l))
            triangulation.legalize_edge(point, (l, j))
            triangulation.legalize_edge(point, (j, k))
            triangulation.legalize_edge(point, (k, i))

    triangulation.remove_outer()
    return list(triangulation.triangles)


def delaunay_triangulation_v2(points):
    '''
    główna funkcja do triangulacji w drugim wariancie
    na podstawie wykładu
    '''
    triangulation = Triangulation()
    triangulation.make_outer_triangle(points)

    shuffle(points)

    for point in points:
        triangle_containing = triangulation.triangle_containing(point)

        a, b, c = triangle_containing
        stack = []
        triangles_to_remove = [triangle_containing]
        triangles_adjacent = triangulation.all_triangles_adjacent(triangle_containing)
        stack += triangles_adjacent
        triangles_visited = [triangle_containing]

        while len(stack) > 0:
            current_triangle = stack.pop()
            triangles_visited.append(current_triangle)

            if triangulation.is_within_circumcircle(current_triangle, point):
                triangles_to_remove.append(current_triangle)
                triangles_adjacent = triangulation.all_triangles_adjacent(current_triangle)
                for triangle in triangles_adjacent:
                    if triangle not in triangles_visited and triangle not in stack:
                        stack.append(triangle)

        triangulation.remove_and_connect(triangles_to_remove, point)
    
    triangulation.remove_outer()
    return list(triangulation.triangles)


