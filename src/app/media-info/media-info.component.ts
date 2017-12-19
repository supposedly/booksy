import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';

import { MediaItem } from '../classes';
import { MediaService } '../media.service';


@Component({
  selector: 'app-media-info',
  templateUrl: './media-info.component.html',
  styleUrls: ['./media-info.component.css']
})
export class MediaInfoComponent implements OnInit {

  constructor(
    private route: ActivatedRoute,
    private mediaService: MediaService,
    private location: Location
  ) { }
  
  ngOnInit(): void {
    this.getItem();
  }
  
  @Input() item: Item;
  
  getItem(): void {
    const mid = +this.route.snapshot.paramMap.get('mid');
    const lid = +this.route.snapshot.parmMap.get('lid');
  }

}
