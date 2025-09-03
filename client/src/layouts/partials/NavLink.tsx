import { Button } from "@mui/material";
import { Link as RouterLink, useLocation } from "react-router-dom";
import React, { FC } from "react";

interface Props {
  to: string;
  text: string;
}

const NavLink: FC<Props> = ({ to, text }) => {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Button
      component={RouterLink}
      to={to}
      variant="text"
      sx={{
        textDecoration: "none",
        padding: "12px 24px",
        color: "white",
        borderRadius: "10px",
        width: "100%",
        display: "flex",
        alignItems: 'center',
        justifyContent: 'flex-start',
        border: isActive ? '2px solid #4B3FD7' : '2px solid transparent',
        background: isActive ? 'rgba(75, 63, 215, 0.3)' : 'rgba(255, 255, 255, 0.05)',
        transition: 'all 0.2s ease-in-out',
        textTransform: 'none',
        fontSize: '1rem',
        fontWeight: isActive ? 600 : 400,
        '&:hover': {
          background: isActive ? "rgba(75, 63, 215, 0.5)" : "rgba(255, 255, 255, 0.1)",
          border: '2px solid #4B3FD7',
        }
      }}
    >
      {text}
    </Button>
  );
};

export default NavLink;
