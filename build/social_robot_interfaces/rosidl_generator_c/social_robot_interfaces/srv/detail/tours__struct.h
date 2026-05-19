// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from social_robot_interfaces:srv/Tours.idl
// generated code does not contain a copyright notice

#ifndef SOCIAL_ROBOT_INTERFACES__SRV__DETAIL__TOURS__STRUCT_H_
#define SOCIAL_ROBOT_INTERFACES__SRV__DETAIL__TOURS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in srv/Tours in the package social_robot_interfaces.
typedef struct social_robot_interfaces__srv__Tours_Request
{
  int64_t idx;
} social_robot_interfaces__srv__Tours_Request;

// Struct for a sequence of social_robot_interfaces__srv__Tours_Request.
typedef struct social_robot_interfaces__srv__Tours_Request__Sequence
{
  social_robot_interfaces__srv__Tours_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} social_robot_interfaces__srv__Tours_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'tour'
#include "geometry_msgs/msg/detail/pose_stamped__struct.h"

/// Struct defined in srv/Tours in the package social_robot_interfaces.
typedef struct social_robot_interfaces__srv__Tours_Response
{
  geometry_msgs__msg__PoseStamped__Sequence tour;
} social_robot_interfaces__srv__Tours_Response;

// Struct for a sequence of social_robot_interfaces__srv__Tours_Response.
typedef struct social_robot_interfaces__srv__Tours_Response__Sequence
{
  social_robot_interfaces__srv__Tours_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} social_robot_interfaces__srv__Tours_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SOCIAL_ROBOT_INTERFACES__SRV__DETAIL__TOURS__STRUCT_H_
