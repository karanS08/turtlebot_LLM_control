// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from social_robot_interfaces:msg/TspCommand.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "social_robot_interfaces/msg/detail/tsp_command__rosidl_typesupport_introspection_c.h"
#include "social_robot_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "social_robot_interfaces/msg/detail/tsp_command__functions.h"
#include "social_robot_interfaces/msg/detail/tsp_command__struct.h"


// Include directives for member types
// Member `waypoints`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__TspCommand_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  social_robot_interfaces__msg__TspCommand__init(message_memory);
}

void social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__TspCommand_fini_function(void * message_memory)
{
  social_robot_interfaces__msg__TspCommand__fini(message_memory);
}

size_t social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__size_function__TspCommand__waypoints(
  const void * untyped_member)
{
  const rosidl_runtime_c__int64__Sequence * member =
    (const rosidl_runtime_c__int64__Sequence *)(untyped_member);
  return member->size;
}

const void * social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__get_const_function__TspCommand__waypoints(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__int64__Sequence * member =
    (const rosidl_runtime_c__int64__Sequence *)(untyped_member);
  return &member->data[index];
}

void * social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__get_function__TspCommand__waypoints(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__int64__Sequence * member =
    (rosidl_runtime_c__int64__Sequence *)(untyped_member);
  return &member->data[index];
}

void social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__fetch_function__TspCommand__waypoints(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const int64_t * item =
    ((const int64_t *)
    social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__get_const_function__TspCommand__waypoints(untyped_member, index));
  int64_t * value =
    (int64_t *)(untyped_value);
  *value = *item;
}

void social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__assign_function__TspCommand__waypoints(
  void * untyped_member, size_t index, const void * untyped_value)
{
  int64_t * item =
    ((int64_t *)
    social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__get_function__TspCommand__waypoints(untyped_member, index));
  const int64_t * value =
    (const int64_t *)(untyped_value);
  *item = *value;
}

bool social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__resize_function__TspCommand__waypoints(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__int64__Sequence * member =
    (rosidl_runtime_c__int64__Sequence *)(untyped_member);
  rosidl_runtime_c__int64__Sequence__fini(member);
  return rosidl_runtime_c__int64__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__TspCommand_message_member_array[1] = {
  {
    "waypoints",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT64,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(social_robot_interfaces__msg__TspCommand, waypoints),  // bytes offset in struct
    NULL,  // default value
    social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__size_function__TspCommand__waypoints,  // size() function pointer
    social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__get_const_function__TspCommand__waypoints,  // get_const(index) function pointer
    social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__get_function__TspCommand__waypoints,  // get(index) function pointer
    social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__fetch_function__TspCommand__waypoints,  // fetch(index, &value) function pointer
    social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__assign_function__TspCommand__waypoints,  // assign(index, value) function pointer
    social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__resize_function__TspCommand__waypoints  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__TspCommand_message_members = {
  "social_robot_interfaces__msg",  // message namespace
  "TspCommand",  // message name
  1,  // number of fields
  sizeof(social_robot_interfaces__msg__TspCommand),
  social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__TspCommand_message_member_array,  // message members
  social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__TspCommand_init_function,  // function to initialize message memory (memory has to be allocated)
  social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__TspCommand_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__TspCommand_message_type_support_handle = {
  0,
  &social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__TspCommand_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_social_robot_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, social_robot_interfaces, msg, TspCommand)() {
  if (!social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__TspCommand_message_type_support_handle.typesupport_identifier) {
    social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__TspCommand_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &social_robot_interfaces__msg__TspCommand__rosidl_typesupport_introspection_c__TspCommand_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
