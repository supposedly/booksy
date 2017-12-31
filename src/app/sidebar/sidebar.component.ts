import { Component, OnInit } from '@angular/core';

import { SideButton } from '../classes';
import { SideButtonService } from '../side-button.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent implements OnInit {
  buttons: SideButton[];
  
  constructor(private sideButtonService: SideButtonService) { }

  ngOnInit() {
    this.getButtons();
  }
  
  getButtons(): void {
    this.sideButtonService.getButtons()
      .subscribe(buttons => this.buttons = buttons);
  }

}
