corner_position_array = np.array(corner_point_array, dtype='f4')
ubo_corner_pos = glGenBuffers(1)
glBindBuffer(GL_UNIFORM_BUFFER, ubo_corner_pos)
glBufferStorage(GL_UNIFORM_BUFFER, corner_position_array.nbytes,
                corner_position_array, GL_DYNAMIC_STORAGE_BIT)
glBindBufferBase(GL_UNIFORM_BUFFER, 1, ubo_corner_pos)