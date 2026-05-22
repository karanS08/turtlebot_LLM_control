// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from social_robot_interfaces:msg/TspCommand.idl
// generated code does not contain a copyright notice

#ifndef SOCIAL_ROBOT_INTERFACES__MSG__DETAIL__TSP_COMMAND__TRAITS_HPP_
#define SOCIAL_ROBOT_INTERFACES__MSG__DETAIL__TSP_COMMAND__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "social_robot_interfaces/msg/detail/tsp_command__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace social_robot_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const TspCommand & msg,
  std::ostream & out)
{
  out << "{";
  // member: waypoints
  {
    if (msg.waypoints.size() == 0) {
      out << "waypoints: []";
    } else {
      out << "waypoints: [";
      size_t pending_items = msg.waypoints.size();
      for (auto item : msg.waypoints) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const TspCommand & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: waypoints
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.waypoints.size() == 0) {
      out << "waypoints: []\n";
    } else {
      out << "waypoints:\n";
      for (auto item : msg.waypoints) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const TspCommand & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace social_robot_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use social_robot_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const social_robot_interfaces::msg::TspCommand & msg,
  std::ostream & out, size_t indentation = 0)
{
  social_robot_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use social_robot_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const social_robot_interfaces::msg::TspCommand & msg)
{
  return social_robot_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<social_robot_interfaces::msg::TspCommand>()
{
  return "social_robot_interfaces::msg::TspCommand";
}

template<>
inline const char * name<social_robot_interfaces::msg::TspCommand>()
{
  return "social_robot_interfaces/msg/TspCommand";
}

template<>
struct has_fixed_size<social_robot_interfaces::msg::TspCommand>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<social_robot_interfaces::msg::TspCommand>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<social_robot_interfaces::msg::TspCommand>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SOCIAL_ROBOT_INTERFACES__MSG__DETAIL__TSP_COMMAND__TRAITS_HPP_
