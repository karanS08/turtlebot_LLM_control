// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from social_robot_interfaces:msg/TspCommand.idl
// generated code does not contain a copyright notice

#ifndef SOCIAL_ROBOT_INTERFACES__MSG__DETAIL__TSP_COMMAND__STRUCT_H_
#define SOCIAL_ROBOT_INTERFACES__MSG__DETAIL__TSP_COMMAND__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'waypoints'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in msg/TspCommand in the package social_robot_interfaces.
typedef struct social_robot_interfaces__msg__TspCommand
{
  rosidl_runtime_c__int64__Sequence waypoints;
} social_robot_interfaces__msg__TspCommand;

// Struct for a sequence of social_robot_interfaces__msg__TspCommand.
typedef struct social_robot_interfaces__msg__TspCommand__Sequence
{
  social_robot_interfaces__msg__TspCommand * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} social_robot_interfaces__msg__TspCommand__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SOCIAL_ROBOT_INTERFACES__MSG__DETAIL__TSP_COMMAND__STRUCT_H_
