import { Component, OnInit } from '@angular/core';

import { NavButton } from '../classes';
import { SideButtonService } from '../head-button.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent implements OnInit {
  buttons: NavButton[];
  
  constructor(private sideButtonService: SideButtonService) { }

  ngOnInit() {
    this.getButtons();
  }
  
  getButtons(): void {
    this.sideButtonService.getButtons()
      .subscribe(buttons => this.buttons = buttons);
  }
  
  selectedButton: NavButton;
  
  onSelect(button: NavButton): void {
    this.selectedButton = button;
  }

}
