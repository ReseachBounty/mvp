import { Flex, Box } from "@chakra-ui/react"
import { createFileRoute, Outlet } from "@tanstack/react-router"

import Navbar from "@/components/Common/Navbar"

export const Route = createFileRoute("/_layout_report")({
  component: Layout,
})

function Layout() {
  return (
    <Flex direction="column" h="100vh">
      <Navbar />
      <Flex flex="1" overflow="hidden">
        <Flex flex="1" direction="column" p={4} overflowY="auto">
          <Outlet />
        </Flex>
      </Flex>
      <Box
        as="footer"
        textAlign="center"
        fontSize="sm"
        borderTop="1px solid"
        py={4}
      >
        © {new Date().getFullYear()} Vastad
      </Box>
    </Flex>
  );
}

export default Layout
